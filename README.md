<<<<<<< HEAD
# PowerTeacher — AI Teacher Brain

Status: **Step 2 of 20 complete** — core schemas and an in-memory teacher-state manager.

## What's here so far

```
ai/teacher/schemas/
├── enums.py    → TeachingAction, TeachingStrategy, DifficultyLevel, StudentLevel, VisualType
├── state.py    → TeacherState (the persistent per-session state machine)
├── actions.py  → TeachingActionOutput (structured LLM/decision output),
│                 StudentAnswerInput, AssessmentResult (interface contract with Person 6)
└── lesson.py   → LessonRequest, LessonPlan, LessonSection (interface contract with frontend)
```

The project now includes validated schemas, in-memory session state with
optimistic concurrency, lesson planning, and an assessment-to-teaching-step
orchestration engine. Later modules (adaptation, misconception handling,
FastAPI routes, and durable storage) can build on these contracts.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run tests

```bash
python -m pytest tests/ -v
```

Expected: all tests pass (currently 34 tests).

## Why these files matter for team integration

- `LessonRequest` / `LessonPlan` — this is the exact JSON shape Person 1
  (frontend) can mock right now to build the classroom UI without waiting
  for the real planner.
- `AssessmentResult` — this is the exact JSON shape Person 6 (assessment)
  must return. Share this file with them today so your modules don't
  drift apart.
- `TeachingActionOutput` — this is what FastAPI (Person 2) will return
  to the frontend on every teaching step.

## Current implementation

`TeacherStepEngine.process_assessment()` accepts an `AssessmentResult`,
updates the session through `TeacherStateManager`, and returns a validated
`TeachingActionOutput` for the next teaching step.
=======
# AI-Powered-Teacher
>>>>>>> 5f5b6a57deaaeb6977e7319faacd1bfed9e7f32d
