import ollama
import json


def check_evidence_sufficiency(question, selected_evidence):

    # Convert selected sentences into text
    evidence_text = "\n".join(
        sentence.text for sentence in selected_evidence
    )

    # Check empty evidence
    if not evidence_text.strip():
        return {
            "self_check": "insufficient",
            "reason": "No selected evidence was provided."
        }

    prompt = f"""
You are an evidence sufficiency evaluator.

Evaluate whether the SELECTED EVIDENCE contains enough
information to answer the QUESTION.

QUESTION:
{question}

SELECTED EVIDENCE:
{evidence_text}

Classification rules:

SUFFICIENT:
The evidence directly answers the main question and covers
its important aspects.

PARTIALLY_SUFFICIENT:
The evidence answers some aspects of the question but
important information is missing.

INSUFFICIENT:
The evidence does not provide enough relevant information
to answer the question.

Important instructions:
1. Evaluate only the selected evidence.
2. Do not use external knowledge.
3. Do not assume information that is not present.
4. Judge the meaning of the evidence, not just keyword presence.
5. Return exactly one classification.

Return valid JSON in this format:

{{
    "self_check": "sufficient",
    "reason": "Brief explanation of the decision."
}}
"""

    try:

        response = ollama.chat(
            model="tinyllama:latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

        result = json.loads(response.message.content)

        classification = result.get("self_check", "").strip().lower()

        allowed_values = {
            "sufficient",
            "partially_sufficient",
            "insufficient"
        }

        if classification not in allowed_values:
            raise ValueError(
                "LLM returned an invalid classification."
            )

        reason = result.get("reason", "No reason provided.")

        return {
            "self_check": classification,
            "reason": reason
        }

    except Exception as error:

        return {
            "self_check": "error",
            "reason": str(error)
        }