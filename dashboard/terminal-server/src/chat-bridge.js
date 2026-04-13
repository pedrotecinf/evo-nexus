/**
 * Chat Bridge — spawns Claude via Agent SDK with structured streaming events.
 * Supports conversation resume via SDK session IDs.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
let sdkModule = null;

/**
 * Parse a .claude/agents/{name}.md file into an AgentDefinition.
 * Extracts YAML frontmatter for metadata and the body as the prompt.
 */
function loadAgentFile(agentName, cwd) {
  const agentPath = path.join(cwd, '.claude', 'agents', `${agentName}.md`);
  if (!fs.existsSync(agentPath)) {
    console.warn(`[chat-bridge] Agent file not found: ${agentPath}`);
    return null;
  }

  const raw = fs.readFileSync(agentPath, 'utf8');
  const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!fmMatch) {
    return { description: agentName, prompt: raw.trim() };
  }

  // Simple YAML frontmatter parser (no dependency needed)
  const fmText = fmMatch[1];
  const meta = {};
  for (const line of fmText.split('\n')) {
    const m = line.match(/^(\w+):\s*(.+)$/);
    if (m) {
      const val = m[2].trim().replace(/^["']|["']$/g, '');
      meta[m[1]] = val;
    }
    // Parse tools list
    if (line.match(/^\s+-\s+\w+/)) {
      if (!meta._lastKey) continue;
      if (!Array.isArray(meta[meta._lastKey])) meta[meta._lastKey] = [];
      meta[meta._lastKey].push(line.trim().replace(/^-\s*/, ''));
    }
    if (line.match(/^\w+:$/)) {
      meta._lastKey = line.replace(':', '').trim();
      meta[meta._lastKey] = [];
    }
  }
  delete meta._lastKey;

  const prompt = fmMatch[2].trim();
  const def = {
    description: typeof meta.description === 'string' ? meta.description : agentName,
    prompt,
  };
  if (meta.model) def.model = meta.model;
  if (Array.isArray(meta.tools)) def.tools = meta.tools;

  return def;
}

async function loadSDK() {
  if (!sdkModule) {
    sdkModule = await import('@anthropic-ai/claude-agent-sdk');
  }
  return sdkModule;
}

class ChatBridge {
  constructor() {
    this.sessions = new Map(); // sessionId -> { query, abortController, active, sdkSessionId }
  }

  async startSession(sessionId, options = {}) {
    const { query: sdkQuery } = await loadSDK();

    const {
      agentName,
      workingDir,
      prompt,
      files,
      sdkSessionId,
      onMessage,
      onError,
      onComplete,
    } = options;

    if (this.sessions.has(sessionId)) {
      await this.stopSession(sessionId);
    }

    const abortController = new AbortController();

    const queryOptions = {
      cwd: workingDir || process.cwd(),
      includePartialMessages: true,
      abortController,
    };

    // Load agent definition from .claude/agents/{name}.md
    if (agentName) {
      const agentDef = loadAgentFile(agentName, queryOptions.cwd);
      if (agentDef) {
        // Use systemPrompt with claude_code preset + agent prompt appended
        queryOptions.systemPrompt = {
          type: 'preset',
          preset: 'claude_code',
          append: agentDef.prompt,
        };
        if (agentDef.model) queryOptions.model = agentDef.model;
        console.log(`[chat-bridge] Loaded agent "${agentName}" via systemPrompt.append (${agentDef.prompt.length} chars, model: ${agentDef.model || 'inherit'})`);
      } else {
        console.warn(`[chat-bridge] Agent "${agentName}" not found, running without agent`);
      }
    }

    queryOptions.allowedTools = [
      'Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep',
      'Agent', 'Skill', 'WebSearch', 'WebFetch',
      'NotebookEdit', 'ToolSearch',
    ];

    // Resume existing conversation if we have an SDK session ID
    if (sdkSessionId) {
      queryOptions.resume = sdkSessionId;
    }

    // Save attached files to temp dir and reference in prompt
    let finalPrompt = prompt || '';
    if (files && files.length > 0) {
      const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'evo-chat-'));
      const savedPaths = [];
      for (const f of files) {
        if (f.base64) {
          const safeName = f.name.replace(/[^a-zA-Z0-9._-]/g, '_');
          const filePath = path.join(tmpDir, safeName);
          fs.writeFileSync(filePath, Buffer.from(f.base64, 'base64'));
          savedPaths.push({ name: f.name, path: filePath, type: f.type });
        }
      }
      if (savedPaths.length > 0) {
        const fileList = savedPaths
          .map(f => `- ${f.name}: ${f.path}`)
          .join('\n');
        const fileNote = `\n\n[Attached files — use Read tool to view them]\n${fileList}`;
        finalPrompt = finalPrompt + fileNote;
      }
    }

    const session = {
      active: true,
      abortController,
      agentName,
      sdkSessionId: sdkSessionId || null,
    };
    this.sessions.set(sessionId, session);

    // Run query in background
    (async () => {
      try {
        console.log(`[chat-bridge] Starting query for session ${sessionId}, agent: ${agentName}, resume: ${sdkSessionId || 'new'}`);
        console.log(`[chat-bridge] Query options:`, JSON.stringify({ cwd: queryOptions.cwd, agent: queryOptions.agent, resume: queryOptions.resume, allowedTools: queryOptions.allowedTools?.length }, null, 2));
        const q = sdkQuery({ prompt: finalPrompt, options: queryOptions });
        console.log(`[chat-bridge] Query created, starting iteration...`);

        for await (const message of q) {
          if (!session.active) break;

          const eventDetail = message.type === 'stream_event' ? ` event=${message.event?.type} cb=${message.event?.content_block?.type || message.event?.delta?.type || ''}` : '';
          if (message.type === 'system') {
            console.log(`[chat-bridge] System message: subtype=${message.subtype}, agent=${message.agent || 'none'}, data=${JSON.stringify(message).slice(0, 200)}`);
          } else {
            console.log(`[chat-bridge] Message received: type=${message.type}${eventDetail}`);
          }

          // Capture SDK session ID from any message that has it
          if (message.session_id && !session.sdkSessionId) {
            session.sdkSessionId = message.session_id;
            if (onMessage) {
              onMessage({ type: 'session_id', sdkSessionId: message.session_id });
            }
          }

          if (onMessage) {
            onMessage(this._transformMessage(message));
          }
        }
        console.log(`[chat-bridge] Query iteration finished for session ${sessionId}`);

        session.active = false;
        this.sessions.delete(sessionId);
        if (onComplete) onComplete({ sdkSessionId: session.sdkSessionId });
      } catch (err) {
        console.error(`[chat-bridge] Error in session ${sessionId}:`, err.message || err);
        session.active = false;
        this.sessions.delete(sessionId);
        if (err.name === 'AbortError') {
          if (onComplete) onComplete({ sdkSessionId: session.sdkSessionId });
        } else {
          if (onError) onError(err);
        }
      }
    })();

    return { sessionId, sdkSessionId: session.sdkSessionId };
  }

  async stopSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    const sdkSessionId = session.sdkSessionId;
    session.active = false;
    try {
      session.abortController.abort();
    } catch {}
    this.sessions.delete(sessionId);
    return { sdkSessionId };
  }

  getSdkSessionId(sessionId) {
    const session = this.sessions.get(sessionId);
    return session?.sdkSessionId || null;
  }

  isActive(sessionId) {
    const session = this.sessions.get(sessionId);
    return session?.active ?? false;
  }

  _transformMessage(msg) {
    switch (msg.type) {
      case 'stream_event': {
        const event = msg.event;
        if (!event) return { type: 'unknown', raw: msg };

        switch (event.type) {
          case 'content_block_start': {
            const cb = event.content_block;
            if (cb?.type === 'tool_use') {
              return {
                type: 'tool_use_start',
                toolName: cb.name,
                toolId: cb.id,
                input: {},
              };
            }
            if (cb?.type === 'text') {
              return { type: 'text_start' };
            }
            if (cb?.type === 'thinking') {
              return { type: 'thinking_start' };
            }
            return { type: 'block_start', blockType: cb?.type };
          }

          case 'content_block_delta': {
            const delta = event.delta;
            if (delta?.type === 'text_delta') {
              return { type: 'text_delta', text: delta.text };
            }
            if (delta?.type === 'input_json_delta') {
              return { type: 'tool_input_delta', json: delta.partial_json };
            }
            if (delta?.type === 'thinking_delta') {
              return { type: 'thinking_delta', text: delta.thinking };
            }
            return { type: 'delta', deltaType: delta?.type };
          }

          case 'content_block_stop': {
            return { type: 'block_stop', index: event.index };
          }

          case 'message_start':
            return { type: 'message_start' };

          case 'message_delta':
            return {
              type: 'message_delta',
              stopReason: event.delta?.stop_reason,
              usage: event.usage,
            };

          case 'message_stop':
            return { type: 'message_stop' };

          default:
            return { type: 'stream_other', eventType: event.type };
        }
      }

      case 'assistant': {
        const content = msg.message?.content || [];
        const blocks = content.map(block => {
          if (block.type === 'text') {
            return { type: 'text', text: block.text };
          }
          if (block.type === 'tool_use') {
            return {
              type: 'tool_use',
              toolName: block.name,
              toolId: block.id,
              input: block.input,
            };
          }
          if (block.type === 'tool_result') {
            return {
              type: 'tool_result',
              toolId: block.tool_use_id,
              content: block.content,
            };
          }
          return { type: block.type };
        });
        return {
          type: 'assistant_message',
          blocks,
          uuid: msg.uuid,
          sessionId: msg.session_id,
        };
      }

      case 'result': {
        return {
          type: 'result',
          subtype: msg.subtype,
          isError: msg.is_error ?? msg.subtype !== 'success',
          durationMs: msg.duration_ms,
          totalCost: msg.total_cost_usd,
          numTurns: msg.num_turns,
          usage: msg.usage,
          errors: msg.errors,
          sessionId: msg.session_id,
        };
      }

      case 'system': {
        return {
          type: 'system',
          subtype: msg.subtype,
          sessionId: msg.session_id,
        };
      }

      default:
        return { type: msg.type || 'unknown', sessionId: msg.session_id };
    }
  }
}

module.exports = { ChatBridge };
