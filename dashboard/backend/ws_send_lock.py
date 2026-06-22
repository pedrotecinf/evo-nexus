"""Serialize all frame writes on a simple_websocket connection.

flask-sock hands each WebSocket route a ``simple_websocket.ws.Server``
instance (subclass of ``simple_websocket.ws.Base``). That class has TWO
threads that write the same socket with NO synchronization:

  1. the application thread(s) calling ``.send()`` / ``.close()`` (our proxies'
     ``_pump_upstream_to_client`` daemon calls ``client_ws.send(...)``, and the
     main bridge thread calls ``client_ws.close()`` in its ``finally``); and
  2. simple-websocket's own internal ``Base._thread``, which replies to client
     Pings with a Pong and sends Close frames via ``_handle_events()``.

Every write site does TWO unguarded steps — ``out = self.ws.send(...)``
(wsproto framing, which mutates a single shared permessage-deflate compressor
with cross-frame Z_SYNC_FLUSH context) then ``self.sock.send(out)``. With two
threads those steps interleave: frames reorder on the wire and, for a large
data frame whose ``sock.send`` spans several write syscalls, a control-frame
write from the other thread can land mid-frame — corrupting the byte stream,
which the browser surfaces as "WebSocket connection failed: Invalid frame
header".

A bridge-only lock is INSUFFICIENT: the internal ``_thread`` bypasses the
bridge and writes Pong/Close directly. So the fix lives on ``Base`` itself.

This wraps the three frame-emitting methods of ``Base`` (``send``, ``close``,
``_handle_events``) so the ``ws.send()`` + ``sock.send()`` pair runs under one
per-instance RLock. The wsproto framing (shared compressor) is held under the
SAME lock as the socket write, so protocol state and wire bytes stay
consistent. RLock is re-entrant so an in-library self-re-entry can't
self-deadlock; no critical section spans a blocking recv/select (those live
OUTSIDE ``_handle_events``), so ``.send()`` is blocked at most for one peer
flush. Idempotent. Import-guarded: no-op if the lib is absent/renamed.
"""

from __future__ import annotations

import threading

_INSTALLED = False


def install() -> None:
    """Monkeypatch simple_websocket.ws.Base to serialize all writes.

    Call once at startup, BEFORE any WebSocket route runs (i.e. before the
    ``flask_sock.Sock`` instance is created). No-op if already patched or if
    simple_websocket is not importable.
    """
    global _INSTALLED
    if _INSTALLED:
        return

    try:
        from simple_websocket.ws import Base
    except Exception:  # lib missing/renamed: leave as-is
        return

    if getattr(Base, "_evonexus_send_lock_installed", False):
        _INSTALLED = True
        return

    _orig_send = Base.send
    _orig_close = Base.close
    _orig_handle_events = Base._handle_events

    def _lock_for(self) -> threading.RLock:
        lock = getattr(self, "_evonexus_send_lock", None)
        if lock is None:
            with Base._evonexus_lock_create_lock:
                lock = getattr(self, "_evonexus_send_lock", None)
                if lock is None:
                    lock = threading.RLock()
                    self._evonexus_send_lock = lock
        return lock

    def send(self, data):
        with _lock_for(self):
            return _orig_send(self, data)

    def close(self, reason=None, message=None):
        with _lock_for(self):
            return _orig_close(self, reason=reason, message=message)

    def _handle_events(self):
        with _lock_for(self):
            return _orig_handle_events(self)

    Base._evonexus_lock_create_lock = threading.Lock()
    Base.send = send
    Base.close = close
    Base._handle_events = _handle_events
    Base._evonexus_send_lock_installed = True
    _INSTALLED = True
