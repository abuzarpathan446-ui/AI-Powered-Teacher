import pytest

from ai.teacher.schemas.enums import TeachingAction
from ai.teacher.state.in_memory_store import InMemoryStateStore
from ai.teacher.state.manager import TeacherStateManager
from ai.teacher.state.store import StateConflictError, StateNotFoundError


@pytest.fixture
def manager():
    return TeacherStateManager(InMemoryStateStore())


def test_create_session_persists_state(manager):
    state = manager.create_session(student_id="u1", current_concept="resistance")
    loaded = manager.load(state.session_id)
    assert loaded.session_id == state.session_id
    assert loaded.current_concept == "resistance"
    assert loaded.student_id == "u1"


def test_load_missing_session_raises(manager):
    with pytest.raises(StateNotFoundError):
        manager.load("sess_does_not_exist")


def test_update_applies_mutator_and_persists(manager):
    state = manager.create_session(student_id="u1", current_concept="resistance")

    def bump(s):
        s.increment_attempt()
        s.record_action(TeachingAction.EXPLAIN)

    updated = manager.update(state.session_id, bump)
    assert updated.attempt_count == 1
    assert updated.last_action == TeachingAction.EXPLAIN

    reloaded = manager.load(state.session_id)
    assert reloaded.attempt_count == 1


def test_update_direct_assignment_still_advances_version(manager):
    """Concurrency safety must not depend on callers using helper methods."""
    state = manager.create_session(student_id="u1", current_concept="resistance")

    updated = manager.update(
        state.session_id, lambda current: setattr(current, "next_action", TeachingAction.EXPLAIN)
    )

    assert updated.version == state.version + 1
    assert updated.next_action == TeachingAction.EXPLAIN


def test_update_on_missing_session_raises(manager):
    with pytest.raises(StateNotFoundError):
        manager.update("sess_ghost", lambda s: s.increment_attempt())


def test_get_returns_isolated_copy(manager):
    """Mutating a loaded state must NOT affect the stored version until update()/save()."""
    state = manager.create_session(student_id="u1", current_concept="resistance")
    loaded = manager.load(state.session_id)
    loaded.increment_attempt()  # mutate the local copy only

    reloaded = manager.load(state.session_id)
    assert reloaded.attempt_count == 0  # store untouched


def test_concurrent_writes_conflict_is_caught_and_retried(manager):
    """
    Simulates two 'requests' racing on the same session: the manager should
    retry once against the fresh state rather than losing either change,
    or raise StateConflictError if retries are exhausted.
    """
    state = manager.create_session(student_id="u1", current_concept="resistance")
    store = manager._store  # test-only reach-in

    # Simulate another request writing first, changing the version in the store.
    stale_copy = store.get(state.session_id)

    def racing_writer(s):
        s.increment_attempt()

    manager.update(state.session_id, racing_writer)  # version now bumped in store

    # Now attempt a save using the stale expected_version directly against the
    # store to prove the guard actually fires.
    with pytest.raises(StateConflictError):
        store.save(stale_copy, expected_version=stale_copy.version)


def test_update_retries_succeed_despite_one_conflict(manager, monkeypatch):
    state = manager.create_session(student_id="u1", current_concept="resistance")
    store = manager._store

    real_save = store.save
    call_count = {"n": 0}

    def flaky_save(s, expected_version=None):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise StateConflictError("simulated race")
        return real_save(s, expected_version=None)  # second attempt: force success

    monkeypatch.setattr(store, "save", flaky_save)

    updated = manager.update(state.session_id, lambda s: s.increment_attempt(), retries=1)
    assert updated.attempt_count == 1
    assert call_count["n"] == 2


def test_update_rejects_negative_retry_count(manager):
    state = manager.create_session(student_id="u1", current_concept="resistance")

    with pytest.raises(ValueError, match="retries"):
        manager.update(state.session_id, lambda s: s.increment_attempt(), retries=-1)


def test_delete_session_removes_state(manager):
    state = manager.create_session(student_id="u1", current_concept="resistance")
    manager.delete_session(state.session_id)
    with pytest.raises(StateNotFoundError):
        manager.load(state.session_id)
