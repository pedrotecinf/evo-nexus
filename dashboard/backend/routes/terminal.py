"""Terminal endpoint — WebSocket PTY for real terminal sessions."""

import os
import pty
import select
import signal
import struct
import fcntl
import termios
import subprocess
import json
import threading
from flask import Blueprint
from flask_login import login_required
from flask_sock import Sock
from routes._helpers import WORKSPACE

bp = Blueprint("terminal", __name__)
sock = Sock()

# Store active sessions: {session_id: {pid, fd}}
sessions = {}
session_counter = 0


def _spawn_pty(cmd, cwd):
    """Spawn a process in a PTY and return (pid, fd)."""
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    env["COLUMNS"] = "120"
    env["LINES"] = "40"

    pid, fd = pty.fork()
    if pid == 0:
        # Child process
        os.chdir(str(cwd))
        os.execvpe(cmd[0], cmd, env)
    return pid, fd


def _set_winsize(fd, rows, cols):
    """Set terminal window size."""
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


@bp.route("/api/terminal/sessions")
@login_required
def list_sessions():
    """List active terminal sessions."""
    result = []
    for sid, info in sessions.items():
        try:
            os.kill(info["pid"], 0)  # Check if alive
            result.append({"id": sid, "cmd": info["cmd"], "alive": True})
        except OSError:
            result.append({"id": sid, "cmd": info["cmd"], "alive": False})
    return {"sessions": result}


@bp.route("/api/terminal/create", methods=["POST"])
@login_required
def create_session():
    """Create a new terminal session."""
    global session_counter
    from flask import request
    data = request.get_json(silent=True) or {}

    cmd_type = data.get("type", "claude")
    if cmd_type == "claude":
        cmd = ["claude", "--dangerously-skip-permissions"]
    elif cmd_type == "shell":
        cmd = [os.environ.get("SHELL", "/bin/zsh")]
    else:
        cmd = ["claude", "--dangerously-skip-permissions"]

    try:
        pid, fd = _spawn_pty(cmd, WORKSPACE)
        session_counter += 1
        sid = f"term-{session_counter}"
        sessions[sid] = {"pid": pid, "fd": fd, "cmd": " ".join(cmd)}
        return {"id": sid, "cmd": " ".join(cmd)}
    except Exception as e:
        return {"error": str(e)}, 500


@bp.route("/api/terminal/kill/<session_id>", methods=["POST"])
@login_required
def kill_session(session_id):
    """Kill a terminal session."""
    info = sessions.get(session_id)
    if not info:
        return {"error": "Session not found"}, 404
    try:
        os.kill(info["pid"], signal.SIGTERM)
        os.close(info["fd"])
    except OSError:
        pass
    del sessions[session_id]
    return {"status": "killed"}


def init_websocket(app):
    """Initialize WebSocket on the Flask app."""
    sock.init_app(app)

    @sock.route("/ws/terminal/<session_id>")
    def terminal_ws(ws, session_id):
        """WebSocket handler for terminal I/O."""
        info = sessions.get(session_id)
        if not info:
            ws.send(json.dumps({"error": "Session not found"}))
            return

        fd = info["fd"]

        # Set non-blocking
        import fcntl
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        def read_output():
            """Read from PTY and send to WebSocket."""
            while True:
                try:
                    r, _, _ = select.select([fd], [], [], 0.1)
                    if r:
                        data = os.read(fd, 4096)
                        if data:
                            ws.send(data.decode("utf-8", errors="replace"))
                        else:
                            break
                except (OSError, EOFError):
                    break
                except Exception:
                    break
            try:
                ws.send("\r\n[Process exited]\r\n")
            except Exception:
                pass

        # Start reader thread
        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()

        # Main loop: read from WebSocket, write to PTY
        try:
            while True:
                try:
                    msg = ws.receive(timeout=300)  # 5 min timeout
                except Exception:
                    break

                if msg is None:
                    break

                # Handle resize messages
                if isinstance(msg, str) and msg.startswith('{"resize":'):
                    try:
                        data = json.loads(msg)
                        rows = data["resize"]["rows"]
                        cols = data["resize"]["cols"]
                        _set_winsize(fd, rows, cols)
                    except Exception:
                        pass
                    continue

                # Handle ping/keepalive
                if isinstance(msg, str) and msg == '{"ping":true}':
                    try:
                        ws.send('{"pong":true}')
                    except Exception:
                        pass
                    continue

                # Write input to PTY
                try:
                    os.write(fd, msg.encode("utf-8") if isinstance(msg, str) else msg)
                except OSError:
                    break
        except Exception:
            pass
        finally:
            reader.join(timeout=1)
