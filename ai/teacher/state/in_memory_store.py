"""
InMemoryStateStore — today's implementation of StateStore.

Backed by a plain dict + a threading.Lock. Good enough for a single-process
hackathon demo; swap for SupabaseStateStore later without touching any
caller, since callers only depend on the StateStore interface.
"""
import threading
from typing import Dict, Optional

from ai.teacher.schemas.state import TeacherState
from ai.teacher.state.store import StateConflictError, StateStore


class InMemoryStateStore(StateStore):
    def __init__(self) -> None:
        self._data: Dict[str, TeacherState] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> Optional[TeacherState]:
        with self._lock:
            state = self._data.get(session_id)
            # Return a copy so callers can't mutate our stored object
            # without going through save() — keeps the concurrency guard honest.
            return state.model_copy(deep=True) if state else None

    def save(self, state: TeacherState, expected_version: Optional[int] = None) -> TeacherState:
        with self._lock:
            existing = self._data.get(state.session_id)
            if expected_version is not None and existing is not None:
                if existing.version != expected_version:
                    raise StateConflictError(
                        f"session {state.session_id}: expected version "
                        f"{expected_version}, store has {existing.version}"
                    )
            # Versioning belongs at the persistence boundary.  This protects
            # updates that assign a field directly instead of using one of
            # TeacherState's convenience helpers.
            stored_copy = state.model_copy(deep=True)
            if existing is not None:
                stored_copy.version = max(existing.version + 1, stored_copy.version)
            self._data[state.session_id] = stored_copy
            return stored_copy.model_copy(deep=True)

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)

    def _clear(self) -> None:
        """Test-only helper."""
        with self._lock:
            self._data.clear()
