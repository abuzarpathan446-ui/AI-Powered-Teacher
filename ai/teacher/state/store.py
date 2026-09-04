"""
StateStore — abstract contract for "somewhere to put a TeacherState".

Only one implementation exists today (InMemoryStateStore). Later, a
SupabaseStateStore can implement this same interface, and nothing in the
planner / strategy engine / adaptation engine has to change — they only
ever talk to TeacherStateManager, never to a concrete store.
"""
from abc import ABC, abstractmethod
from typing import Optional

from ai.teacher.schemas.state import TeacherState


class StateStore(ABC):
    @abstractmethod
    def get(self, session_id: str) -> Optional[TeacherState]:
        """Return the state for session_id, or None if it doesn't exist."""

    @abstractmethod
    def save(self, state: TeacherState, expected_version: Optional[int] = None) -> TeacherState:
        """
        Persist state. If expected_version is given, the save must fail with
        StateConflictError when the stored version doesn't match — this is
        the optimistic-concurrency guard against two requests clobbering
        each other's writes.
        """

    @abstractmethod
    def delete(self, session_id: str) -> None:
        """Remove a session's state. No-op if it doesn't exist."""


class StateNotFoundError(KeyError):
    """Raised when a session_id has no stored state."""


class StateConflictError(RuntimeError):
    """
    Raised when save() is called with an expected_version that doesn't match
    the version currently in the store — i.e. someone else wrote to this
    session's state since we last read it.
    """
