import os
import time
from typing import Callable, Dict, Optional

from groq import Groq


MODEL_FAST = "openai/gpt-oss-20b"
MODEL_STRONG = "openai/gpt-oss-120b"

MAX_RETRIES = 3


class WorkflowError(Exception):
    """Raised when a study-pack workflow stage fails."""


def get_api_key() -> str:
    """
    Get the Groq API key from Streamlit Secrets first,
    then from an environment variable.
    """

    try:
        import streamlit as st

        if "GROQ_API_KEY" in st.secrets:
            key = st.secrets["GROQ_API_KEY"]

            if key:
                return key

    except Exception:
        pass

    key = os.getenv("GROQ_API_KEY")

    if key:
        return key

    raise WorkflowError(
        "GROQ_API_KEY is missing. "
        "Add it to Streamlit Secrets or your environment."
    )


def get_client() -> Groq:
    """Create a Groq client."""
    return Groq(api_key=get_api_key())


def call_groq(prompt: str, model: str, stage_name: str) -> str:
    """
    Call Groq with retry-based error handling.
    """

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = get_client().chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a careful educational AI. "
                            "Follow the requested format, do not invent facts, "
                            "and keep content appropriate for the requested level."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.3,
            )

            text = response.choices[0].message.content

            if not text or not text.strip():
                raise ValueError(
                    "The model returned an empty response."
                )

            return text.strip()

        except Exception as exc:

            last_error = exc

            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt - 1))

    raise WorkflowError(
        f"Stage '{stage_name}' failed after "
        f"{MAX_RETRIES} attempts. "
        "Please try again. If the problem continues, "
        "check your Groq API key and model availability."
    ) from last_error


# ============================================================
# STAGE 1 — PLANNING
# ============================================================

def create_plan(
    subject,
    topic,
    level,
    study_days,
    language
):

    prompt = f"""
Create a personalized study plan.

Subject: {subject}
Topic: {topic}
Student level: {level}
Available study days: {study_days}
Output language: {language}

Return:

1. Learning objectives
2. Prerequisites
3. Main concepts in a logical order
4. Day-by-day study plan
5. Practice strategy
6. Revision strategy

Keep the plan realistic for the available number of days.
"""

    return call_groq(
        prompt,
        MODEL_FAST,
        "Planning"
    )


# ============================================================
# STAGE 2 — CONTENT GENERATION
# ============================================================

def generate_content(
    subject,
    topic,
    level,
    language,
    plan
):

    prompt = f"""
Generate clear study content using the plan below.

Subject: {subject}
Topic: {topic}
Student level: {level}
Output language: {language}

PLAN:
{plan}

Include:

1. Simple explanation
2. Important concepts
3. Key definitions
4. Examples
5. Common mistakes
6. Quick revision points

Do not add unrelated material.
"""

    return call_groq(
        prompt,
        MODEL_STRONG,
        "Content generation"
    )


# ============================================================
# STAGE 3 — ASSESSMENT
# ============================================================

def generate_assessment(
    subject,
    topic,
    level,
    language,
    content
):

    prompt = f"""
Create an assessment based ONLY on the study content below.

Subject: {subject}
Topic: {topic}
Student level: {level}
Output language: {language}

CONTENT:
{content}

Create:

- 5 MCQs with A-D options and clearly marked answers
- 5 short-answer questions
- 3 conceptual/practice questions

Make the difficulty appropriate for the student level.

Do not ask questions that are unsupported by the content.
"""

    return call_groq(
        prompt,
        MODEL_FAST,
        "Assessment"
    )


# ============================================================
# STAGE 4 — REVIEW
# ============================================================

def review_pack(
    subject,
    topic,
    level,
    content,
    assessment
):

    prompt = f"""
Review this educational study pack for quality.

Subject: {subject}
Topic: {topic}
Student level: {level}

CONTENT:
{content}

ASSESSMENT:
{assessment}

Check:

1. Factual consistency
2. Missing important concepts
3. Duplicate or ambiguous questions
4. Questions unsupported by the content
5. Level appropriateness
6. Clarity

For each issue, provide a correction.

If there are no issues, say so clearly.
"""

    return call_groq(
        prompt,
        MODEL_STRONG,
        "Review"
    )


# ============================================================
# STAGE 5 — FINAL REFINEMENT
# ============================================================

def refine_pack(
    subject,
    topic,
    level,
    study_days,
    language,
    plan,
    content,
    assessment,
    review
):

    prompt = f"""
Create the final personalized study pack.

Subject: {subject}
Topic: {topic}
Student level: {level}
Study days: {study_days}
Output language: {language}

PLAN:
{plan}

CONTENT:
{content}

ASSESSMENT:
{assessment}

REVIEW:
{review}

Apply valid corrections from the review.

Return a clean Markdown study pack with:

# 📚 Study Pack

## 1. Learning Objectives

## 2. Study Notes

## 3. Important Concepts

## 4. Examples

## 5. Quick Revision

## 6. MCQs

## 7. Short Questions

## 8. Practice Questions

## 9. Study Plan

## 10. Final Exam Tips

Do not mention this internal workflow.
"""

    return call_groq(
        prompt,
        MODEL_STRONG,
        "Final refinement"
    )


# ============================================================
# COMPLETE WORKFLOW
# ============================================================

def generate_study_pack(
    subject: str,
    topic: str,
    level: str,
    study_days: int,
    language: str,
    progress_callback: Optional[
        Callable[[str, int], None]
    ] = None
) -> Dict[str, str]:

    def progress(message, percent):

        if progress_callback:
            progress_callback(
                message,
                percent
            )

    # ---------------------------
    # Stage 1
    # ---------------------------

    progress(
        "Stage 1/5 — Planning...",
        10
    )

    plan = create_plan(
        subject,
        topic,
        level,
        study_days,
        language
    )

    # ---------------------------
    # Stage 2
    # ---------------------------

    progress(
        "Stage 2/5 — Generating content...",
        30
    )

    content = generate_content(
        subject,
        topic,
        level,
        language,
        plan
    )

    # ---------------------------
    # Stage 3
    # ---------------------------

    progress(
        "Stage 3/5 — Creating assessment...",
        50
    )

    assessment = generate_assessment(
        subject,
        topic,
        level,
        language,
        content
    )

    # ---------------------------
    # Stage 4
    # ---------------------------

    progress(
        "Stage 4/5 — Reviewing...",
        70
    )

    review = review_pack(
        subject,
        topic,
        level,
        content,
        assessment
    )

    # ---------------------------
    # Stage 5
    # ---------------------------

    progress(
        "Stage 5/5 — Refining final pack...",
        90
    )

    final_pack = refine_pack(
        subject,
        topic,
        level,
        study_days,
        language,
        plan,
        content,
        assessment,
        review
    )

    return {
        "plan": plan,
        "content": content,
        "assessment": assessment,
        "review": review,
        "final_pack": final_pack,
          }
