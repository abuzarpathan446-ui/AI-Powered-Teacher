"""
TeacherStateManager — the only thing other modules should talk to for
reading/writing session state. They never touch a StateStore directly.

    create_session()  -> new TeacherState, persisted
    load(session_id)  -> current TeacherState (raises if missing)
    update(session_id, mutator_fn) -> safely apply a change, retrying once
                                       on a concurrency conflict
"""
from typing import Callable, Optional

from ai.teacher.schemas.enums import Difficulty, Language, StudentLevel
from ai.teacher.schemas.state import TeacherState
from ai.teacher.state.store import StateConflictError, StateNotFoundError, StateStore

MutatorFn = Callable[[TeacherState], None]


class TeacherStateManager:
    def __init__(self, store: StateStore):
        self._store = store

    def create_session(
        self,
        student_id: str,
        current_concept: str,
        *,
        difficulty: Difficulty = Difficulty.EASY,
        language: Language = Language.ENGLISH,
        student_level: StudentLevel = StudentLevel.BEGINNER,
        time_remaining_minutes: Optional[float] = None,
    ) -> TeacherState:
        state = TeacherState(
            student_id=student_id,
            current_concept=current_concept,
            difficulty=difficulty,
            language=language,
            student_level=student_level,
            time_remaining_minutes=time_remaining_minutes,
        )
        return self._store.save(state)

    def load(self, session_id: str) -> TeacherState:
        state = self._store.get(session_id)
        if state is None:
            raise StateNotFoundError(f"no state found for session {session_id}")
        return state

    def update(self, session_id: str, mutator: MutatorFn, *, retries: int = 1) -> TeacherState:
        """
        Load current state, apply `mutator` in place (it should call the
        TeacherState helper methods — record_action, apply_mastery_delta,
        etc.), then save with an optimistic-concurrency check.

        On a StateConflictError (another request wrote first), reload and
        retry the mutation up to `retries` times before giving up. This
        keeps two simultaneous student events from silently overwriting
        each other's state changes.
        """
        if retries < 0:
            raise ValueError("retries must be greater than or equal to zero")

        attempts_left = retries + 1
        last_error: Optional[StateConflictError] = None

        while attempts_left > 0:
            state = self.load(session_id)
            expected_version = state.version
            mutator(state)
            try:
                return self._store.save(state, expected_version=expected_version)
            except StateConflictError as e:
                last_error = e
                attempts_left -= 1

        assert last_error is not None
        raise last_error

    def delete_session(self, session_id: str) -> None:
        self._store.delete(session_id)
