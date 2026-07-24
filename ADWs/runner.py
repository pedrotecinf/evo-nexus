#!/usr/bin/env python3
"""
Core runner for ADWs — executes Claude Code CLI with agents, visual output, logs and Telegram notification.
"""

import fcntl
import subprocess
import os
import sys
import json
import queue
import signal
import threading
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "yellow",
    "error": "bold red",
    "step": "bold blue",
    "dim": "dim white",
})

console = Console(theme=theme)

WORKSPACE = Path(__file__).parent.parent
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def _timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _parse_usage(json_result: dict) -> dict:
    """Extract token and cost data from Claude CLI JSON result."""
    usage = json_result.get("usage", {})
    return {
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
        "cost_usd": (
            json_result["total_cost_usd"]
            if json_result.get("total_cost_usd") is not None
            else usage.get("cost_usd", 0)
        ),
    }


def _save_metrics(log_name, duration, returncode, agent, stdout, usage=None):
    """Save accumulated metrics per routine in metrics.json."""
    metrics_file = LOGS_DIR / "metrics.json"
    lock_file = LOGS_DIR / "metrics.json.lock"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    with open(lock_file, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            try:
                metrics = json.loads(metrics_file.read_text()) if metrics_file.exists() else {}
            except (json.JSONDecodeError, OSError):
                metrics = {}

            if log_name not in metrics:
                metrics[log_name] = {
                    "runs": 0, "successes": 0, "failures": 0,
                    "total_duration": 0, "total_cost_usd": 0,
                    "total_input_tokens": 0, "total_output_tokens": 0,
                    "total_cache_creation_tokens": 0, "total_cache_read_tokens": 0,
                    "last_run": None, "last_status": None, "last_agent": None,
                }

            m = metrics[log_name]
            m["runs"] += 1
            m["total_duration"] += duration
            m["last_run"] = datetime.now().isoformat()
            m["last_status"] = "success" if returncode == 0 else "failure"
            m["last_agent"] = agent or "default"
            if returncode == 0:
                m["successes"] += 1
            else:
                m["failures"] += 1

            if usage:
                m["total_cost_usd"] += usage.get("cost_usd", 0)
                m["total_input_tokens"] += usage.get("input_tokens", 0)
                m["total_output_tokens"] += usage.get("output_tokens", 0)
                m["total_cache_creation_tokens"] += usage.get("cache_creation_tokens", 0)
                m["total_cache_read_tokens"] += usage.get("cache_read_tokens", 0)

            tmp_file = metrics_file.with_suffix(f".{os.getpid()}.tmp")
            tmp_file.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
            os.replace(tmp_file, metrics_file)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _log_to_file(log_name, prompt, stdout, stderr, returncode, duration, usage=None):
    """Save structured log in JSONL and a detailed local file."""
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "run": log_name,
        "prompt": prompt[:500],
        "returncode": returncode,
        "duration_seconds": round(duration, 1),
        "stdout_lines": len(stdout.splitlines()),
        "stderr_lines": len(stderr.splitlines()),
    }
    if usage:
        entry["input_tokens"] = usage["input_tokens"]
        entry["output_tokens"] = usage["output_tokens"]
        entry["cost_usd"] = round(usage["cost_usd"], 5)
    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    detail_dir = LOGS_DIR / "detail"
    detail_dir.mkdir(exist_ok=True)
    detail_file = detail_dir / f"{_timestamp()}-{log_name}.log"
    with open(detail_file, "w") as f:
        f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
        f.write(f"DURATION: {duration:.1f}s\n")
        f.write(f"RETURNCODE: {returncode}\n")
        f.write(f"PROMPT:\n{prompt}\n\n")
        f.write(f"{'=' * 60}\nSTDOUT:\n{'=' * 60}\n{stdout}\n\n")
        if stderr:
            f.write(f"{'=' * 60}\nSTDERR:\n{'=' * 60}\n{stderr}\n")


def _spawn_cli(cli_command: str, prompt: str, agent: str | None, provider_env: dict,
               profile: str | None = None) -> subprocess.Popen:
    """Spawn a CLI process using only hardcoded command strings.

    Uses a dictionary lookup so that the subprocess argument is always
    a static string, satisfying semgrep/opengrep subprocess injection rules.

    ``profile`` (Hermes only) selects the Hermes profile per-invocation via the
    adapter's ``--profile`` flag; ignored by the claude/openclaude branches.
    """
    base_args = ["--print", "--dangerously-skip-permissions", "--output-format", "json"]
    if agent:
        base_args.extend(["--agent", agent])
    base_args.append(prompt)

    env = {**os.environ, **provider_env, "TERM": "dumb"}
    popen_kwargs = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(WORKSPACE),
        env=env,
        # Keep every CLI invocation in an isolated process group. This lets the
        # timeout path terminate the CLI plus any Hermes adapter descendants.
        start_new_session=True,
    )

    # Hardcoded dispatch — each branch uses a literal string for the executable
    if cli_command == "hermes":
        # Use the Hermes adapter wrapper for consistent JSON output
        adapter_path = Path(__file__).parent / "hermes_adapter.py"
        hermes_args = [
            "--print",
            "--output-format", "json",
            "--dangerously-skip-permissions",
        ]
        if agent:
            hermes_args.extend(["--agent", agent])
        if profile:
            hermes_args.extend(["--profile", profile])
        hermes_args.append(prompt)
        return subprocess.Popen([sys.executable, str(adapter_path)] + hermes_args, **popen_kwargs)  # noqa: S603
    elif cli_command == "openclaude":
        return subprocess.Popen(["openclaude"] + base_args, **popen_kwargs)  # noqa: S603
    else:
        return subprocess.Popen(["claude"] + base_args, **popen_kwargs)  # noqa: S603
_ALLOWED_CLI_COMMANDS = frozenset({"claude", "openclaude", "hermes"})
_ALLOWED_ENV_VARS = frozenset({
    "CLAUDE_CODE_USE_OPENAI", "CLAUDE_CODE_USE_GEMINI", "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX", "OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL",
    # Codex OAuth support (OpenClaude 0.3+ auto-reads ~/.codex/auth.json)
    "CODEX_AUTH_JSON_PATH", "CODEX_API_KEY",
    "GEMINI_API_KEY", "GEMINI_MODEL", "AWS_REGION", "AWS_BEARER_TOKEN_BEDROCK",
    "ANTHROPIC_VERTEX_PROJECT_ID", "CLOUD_ML_REGION",
    # Hermes support
    "AGENT_MAX_TURNS", "HERMES_MODEL", "HERMES_PROVIDER", "HERMES_API_KEY",
    "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY",
})


def _kill_process_group(process: subprocess.Popen, grace: float = 1.0) -> None:
    """Terminate a CLI process and every descendant in its process group."""
    if process.poll() is not None:
        return

    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except ProcessLookupError:
        return

    try:
        process.wait(timeout=grace)
        return
    except subprocess.TimeoutExpired:
        pass

    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass


def _get_provider_config() -> tuple[str, dict]:
    """Read active provider CLI command and env vars from config/providers.json.

    Only allowlisted CLI commands and env var names are returned.
    For OpenAI-based providers, injects a sensible default OPENAI_MODEL when
    missing — 'codexplan' for Codex OAuth, 'gpt-4.1' for plain API key mode.
    """
    config_path = WORKSPACE / "config" / "providers.json"
    if not config_path.is_file():
        return "claude", {}
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        active = config.get("active_provider", "anthropic")
        provider = config.get("providers", {}).get(active, {})
        cli = provider.get("cli_command", "claude")
        if cli not in _ALLOWED_CLI_COMMANDS:
            cli = "claude"
        env_vars = {
            k: v for k, v in provider.get("env_vars", {}).items()
            if v and k in _ALLOWED_ENV_VARS
        }
        # Codex OAuth: OpenClaude expects 'codexplan' / 'codexspark' aliases
        # to route to the Codex backend. A raw gpt-5.x string bypasses Codex.
        if not env_vars.get("OPENAI_MODEL"):
            if active == "codex_auth":
                env_vars["OPENAI_MODEL"] = "codexplan"
            elif active == "openai":
                env_vars["OPENAI_MODEL"] = "gpt-4.1"
        return cli, env_vars
    except (json.JSONDecodeError, OSError):
        return "claude", {}


def run_claude(prompt: str, log_name: str = "unnamed", timeout: int = 600, agent: str = None,
               profile: str = None) -> dict:
    """
    Execute AI CLI (claude, openclaude, or hermes) with streaming output.

    Uses the active provider from config/providers.json to determine
    which binary to run and which env vars to inject.

    Args:
        prompt: The prompt to execute
        log_name: Name for logs
        timeout: Timeout in seconds
        agent: Agent name (.claude/agents/*.md) — if None, runs without agent
        profile: Hermes profile slug (privilege routing). Only used when the
            active provider is Hermes; ignored otherwise. If None, Hermes runs
            under its global active profile (backward-compatible).
    """
    cli_command, provider_env = _get_provider_config()

    if agent:
        agent_label = f"@{agent}"
    else:
        agent_label = ""
    provider_label = f"[{cli_command}]" if cli_command != "claude" else ""
    console.print(f"  [step]▶[/step] {log_name} [dim]{agent_label} {provider_label}[/dim]", end="")

    start_time = datetime.now()

    try:
        process = _spawn_cli(cli_command, prompt, agent, provider_env, profile)

        stdout_lines = []
        line_count = 0

        # Thread-safe line reader: drain stdout without blocking the main thread.
        # The reader thread exits when the process closes stdout or when the
        # deadline elapses — whichever comes first.
        #
        # Previously (buggy):
        #   for line in process.stdout:      # blocks forever if CLI hangs
        #       stdout_lines.append(line)     # without closing stdout
        #   process.wait(timeout=timeout)    # only reached after EOF — timeout never fires
        #
        # Fix: reader thread feeds a Queue; main thread enforces deadline per-read.
        # If no new line arrives within _LINE_TIMEOUT, the deadline is checked;
        # if the overall deadline is past, we kill the process and return TimeoutExpired.
        # _LINE_TIMEOUT must be strictly less than `timeout` so the deadline has a
        # chance to fire before Python aborts the whole process.

        _LINE_TIMEOUT = 2  # seconds between lines before checking overall deadline
        _reader_queue: queue.Queue = queue.Queue()
        _deadline = time.monotonic() + timeout

        def _reader_thread(stream, tag):
            try:
                for raw_line in iter(stream.readline, ""):
                    _reader_queue.put((tag, raw_line))
            finally:
                _reader_queue.put((f"{tag}_eof", None))

        stdout_thread = threading.Thread(
            target=_reader_thread, args=(process.stdout, "stdout"), daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_reader_thread, args=(process.stderr, "stderr"), daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

        stderr_lines = []
        stdout_done = False
        stderr_done = False
        deadline_fired = False
        while not (stdout_done and stderr_done):
            remaining = _deadline - time.monotonic()
            if remaining <= 0:
                deadline_fired = True
                break
            try:
                tag, data = _reader_queue.get(timeout=min(_LINE_TIMEOUT, remaining))
            except queue.Empty:
                continue

            if tag == "stdout_eof":
                stdout_done = True
            elif tag == "stderr_eof":
                stderr_done = True
            elif tag == "stdout":
                stdout_lines.append(data)
                line_count += 1
            else:
                stderr_lines.append(data)

        if deadline_fired:
            _kill_process_group(process)
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            duration = (datetime.now() - start_time).total_seconds()
            stderr = "".join(stderr_lines)
            stderr = f"Timeout after {timeout}s" + (f"\n{stderr}" if stderr else "")
            console.print(f"\r  [error]✗[/error] {log_name} [warning](timeout {timeout}s)[/warning]")
            _log_to_file(log_name, prompt, "", stderr, -1, duration)
            return {"success": False, "stdout": "", "stderr": stderr, "returncode": -1, "duration": duration}

        try:
            process.wait(timeout=max(0, _deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            _kill_process_group(process)
            duration = (datetime.now() - start_time).total_seconds()
            stderr = f"Timeout after {timeout}s"
            console.print(f"\r  [error]✗[/error] {log_name} [warning](timeout {timeout}s)[/warning]")
            _log_to_file(log_name, prompt, "", stderr, -1, duration)
            return {"success": False, "stdout": "", "stderr": stderr, "returncode": -1, "duration": duration}

        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        stderr = "".join(stderr_lines)
        stdout = "".join(stdout_lines)
        duration = (datetime.now() - start_time).total_seconds()

        # Parse JSON output to extract result and usage
        usage = None
        result_text = stdout
        try:
            json_result = json.loads(stdout)
            usage = _parse_usage(json_result)
            result_text = json_result.get("result", stdout)
        except (json.JSONDecodeError, TypeError):
            pass

        full_prompt = f"[agent:{agent}] {prompt}" if agent else prompt
        _log_to_file(log_name, full_prompt, result_text, stderr, process.returncode, duration, usage)
        _save_metrics(log_name, duration, process.returncode, agent, result_text, usage)

        if process.returncode == 0:
            cost_str = ""
            if usage:
                tokens_total = usage["input_tokens"] + usage["output_tokens"]
                cost_str = f" | {tokens_total:,}tok | ${usage['cost_usd']:.2f}"
            console.print(f"\r  [success]✓[/success] {log_name} [dim]({duration:.0f}s{cost_str})[/dim]")
        else:
            console.print(f"\r  [error]✗[/error] {log_name} [dim](exit {process.returncode}, {duration:.0f}s)[/dim]")
            if stderr:
                for err_line in stderr.strip().splitlines()[:3]:
                    console.print(f"    [error]{err_line}[/error]")

        return {
            "success": process.returncode == 0,
            "stdout": result_text,
            "stderr": stderr,
            "returncode": process.returncode,
            "duration": duration,
            "usage": usage,
        }

    except subprocess.TimeoutExpired:
        _kill_process_group(process)
        duration = (datetime.now() - start_time).total_seconds()
        console.print(f"\r  [error]✗[/error] {log_name} [warning](timeout {timeout}s)[/warning]")
        _log_to_file(log_name, prompt, "", f"Timeout after {timeout}s", -1, duration)
        return {"success": False, "stdout": "", "stderr": f"Timeout after {timeout}s", "returncode": -1, "duration": duration}

    except KeyboardInterrupt:
        _kill_process_group(process)
        duration = (datetime.now() - start_time).total_seconds()
        console.print(f"\n  [warning]⚠ Cancelled by user[/warning]")
        _log_to_file(log_name, prompt, "", "Cancelled by user", -2, duration)
        raise

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        console.print(f"\r  [error]✗[/error] {log_name} [error]({e})[/error]")
        _log_to_file(log_name, prompt, "", str(e), -3, duration)
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -3, "duration": duration}


def run_skill(
    skill_name: str,
    args: str = "",
    log_name: str = None,
    timeout: int = 600,
    agent: str = None,
    notify_telegram: bool | str = False,
    profile: str = None,
) -> dict:
    """Execute a skill via CLI, optionally with an agent.

    Args:
        notify_telegram: Controls post-skill Telegram notification.
            False (default) — no notification.
            True            — Python sends ONE Telegram after the skill; reads
                              chat_id from TELEGRAM_CHAT_ID env var.
            "<chat_id>"     — same as True but overrides the chat_id.

    The agent is asked to output a line "TELEGRAM_MSG: <text>" in its stdout.
    Python reads that line and calls send_telegram() exactly once.
    The agent NEVER calls the Telegram MCP tool directly.
    """
    chat_id = None
    if notify_telegram:
        chat_id = (
            notify_telegram
            if isinstance(notify_telegram, str)
            else os.environ.get("TELEGRAM_CHAT_ID", "")
        ) or None

    prompt = f"Execute the skill /{skill_name} {args}".strip()
    if chat_id:
        prompt += (
            f"\n\n---\n"
            f"Ao finalizar, escreva na última linha do output:\n"
            f"TELEGRAM_MSG: [emoji] [nome da rotina] [data] | [resultado 1] | [resultado 2]\n"
            f"Apenas UMA linha TELEGRAM_MSG:. NÃO use a ferramenta Telegram/reply — "
            f"o sistema Python lê essa linha e envia a notificação automaticamente.\n"
            f"---"
        )

    result = run_claude(prompt, log_name or skill_name, timeout, agent=agent, profile=profile)

    if chat_id and result.get("returncode", -1) == 0:
        stdout = result.get("stdout", "")
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if line.startswith("TELEGRAM_MSG:"):
                msg = line[len("TELEGRAM_MSG:"):].strip()
                if msg:
                    send_telegram(msg, chat_id=chat_id)
                break  # only ever send one message

    return result


def run_script(func, log_name: str = "unnamed", timeout: int = 120) -> dict:
    """
    Execute a pure Python function (no Claude CLI, no AI, no tokens).
    Same logging/metrics as run_claude but with cost=0.

    Args:
        func: Callable that returns {"ok": bool, "summary": str, "data": ...}
        log_name: Name for logs
        timeout: Timeout in seconds
    """
    console.print(f"  [step]▶[/step] {log_name} [dim]systematic[/dim]", end="")
    start_time = datetime.now()

    try:
        import signal

        def _timeout_handler(signum, frame):
            raise TimeoutError(f"Timeout after {timeout}s")

        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)

        try:
            result = func()
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

        duration = (datetime.now() - start_time).total_seconds()
        ok = result.get("ok", True) if isinstance(result, dict) else bool(result)
        summary_text = result.get("summary", str(result)) if isinstance(result, dict) else str(result)
        returncode = 0 if ok else 1

        _log_to_file(log_name, f"[systematic] {log_name}", summary_text, "", returncode, duration)
        _save_metrics(log_name, duration, returncode, "system", summary_text)

        if ok:
            console.print(f"\r  [success]✓[/success] {log_name} [dim]({duration:.1f}s | {summary_text})[/dim]")
        else:
            console.print(f"\r  [error]✗[/error] {log_name} [dim]({duration:.1f}s | {summary_text})[/dim]")

        return {
            "success": ok,
            "stdout": summary_text,
            "stderr": "",
            "returncode": returncode,
            "duration": duration,
            "usage": None,
        }

    except TimeoutError:
        duration = (datetime.now() - start_time).total_seconds()
        console.print(f"\r  [error]✗[/error] {log_name} [warning](timeout {timeout}s)[/warning]")
        _log_to_file(log_name, f"[systematic] {log_name}", "", f"Timeout after {timeout}s", -1, duration)
        return {"success": False, "stdout": "", "stderr": f"Timeout after {timeout}s", "returncode": -1, "duration": duration}

    except KeyboardInterrupt:
        duration = (datetime.now() - start_time).total_seconds()
        console.print(f"\n  [warning]⚠ Cancelled by user[/warning]")
        raise

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        console.print(f"\r  [error]✗[/error] {log_name} [error]({e})[/error]")
        _log_to_file(log_name, f"[systematic] {log_name}", "", str(e), -3, duration)
        _save_metrics(log_name, duration, -3, "system", str(e))
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -3, "duration": duration}


def banner(title: str, subtitle: str = "", color: str = "cyan"):
    content = f"[bold white]{title}[/bold white]"
    if subtitle:
        content += f"\n[dim]{subtitle}[/dim]"
    console.print(Panel(content, border_style=color, padding=(0, 2)))


def summary(results: list, title: str = "Completed"):
    """Show final summary in terminal."""
    total_duration = sum(r.get("duration", 0) for r in results)
    success = sum(1 for r in results if r.get("success"))
    failed = len(results) - success

    total_cost = sum(r.get("usage", {}).get("cost_usd", 0) for r in results if r.get("usage"))
    total_tokens = sum(
        (r.get("usage", {}).get("input_tokens", 0) + r.get("usage", {}).get("output_tokens", 0))
        for r in results if r.get("usage")
    )

    status = "[success]✅ All OK[/success]" if failed == 0 else f"[warning]⚠ {failed} failure(s)[/warning]"
    cost_line = f" | {total_tokens:,} tokens | ${total_cost:.2f}" if total_tokens > 0 else ""
    console.print(Panel(
        f"{status}\n[dim]Steps: {success}/{len(results)} | Tempo: {total_duration:.0f}s{cost_line}[/dim]",
        title=f"[bold]{title}[/bold]",
        border_style="green" if failed == 0 else "yellow",
        padding=(0, 2)
    ))


def send_telegram(text: str, chat_id: str = None) -> bool:
    """Send a Telegram message via bot API (no MCP dependency).

    Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from environment.
    Returns True if sent successfully, False otherwise.
    """
    import urllib.request
    import urllib.parse

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    cid = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not cid:
        console.print("  [warning]⚠ Telegram not configured (missing BOT_TOKEN or CHAT_ID)[/warning]")
        return False

    try:
        payload = urllib.parse.urlencode({"chat_id": cid, "text": text, "parse_mode": "HTML"}).encode()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        req = urllib.request.Request(url, data=payload, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            ok = resp.status == 200
        if ok:
            console.print("  [success]✓[/success] Telegram enviado")
        else:
            console.print(f"  [warning]⚠ Telegram status {resp.status}[/warning]")
        return ok
    except Exception as e:
        console.print(f"  [warning]⚠ Telegram error: {e}[/warning]")
        return False
