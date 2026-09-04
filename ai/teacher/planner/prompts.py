"""Versioned prompt construction for lesson planning."""
from ai.teacher.schemas.lesson import LessonRequest

SYSTEM_INSTRUCTIONS = """You are an expert instructional designer. Create a rigorous, learner-centred lesson plan for any educational domain. Infer concepts, prerequisites, sequence, teaching strategies, and assessment points from the topic and context. Return only data matching the requested LessonPlan schema; do not invent a fixed subject template."""
PROMPT_VERSION = "1.0"

def build_lesson_plan_prompt(request: LessonRequest) -> str:
    def join(values: list[str]) -> str:
        return ", ".join(values) if values else "none provided"
    return f"""{SYSTEM_INSTRUCTIONS}

Topic: {request.topic}
Student level: {request.student_level.value}
Preferred language: {request.language.value}
Learning goal: {request.learning_goal or 'not specified'}
Available time (minutes): {request.time_budget_minutes if request.time_budget_minutes is not None else 'not specified'}
Current mastery: {request.current_mastery if request.current_mastery is not None else 'not specified'}
Known concepts: {join(request.known_concepts)}
Weak concepts: {join(request.weak_concepts)}
Learning history: {join(request.learning_history)}
Optional grounding context: {request.rag_context or 'none provided'}

Plan schema: LessonPlan (planner_version={PROMPT_VERSION})."""
