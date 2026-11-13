import ollama


# -----------------------------------------
# ROUTE 1: DIRECT
# -----------------------------------------

def direct_route(question, selected_evidence, solver):

    evidence_text = "\n".join(
        sentence.text for sentence in selected_evidence
    )

    answer = solver(question, evidence_text)

    return {
        "route": "direct",
        "answer": answer,
        "widen_attempts": 0
    }


# -----------------------------------------
# ROUTE 2: RECITE-THEN-SOLVE
# -----------------------------------------

def recite_route(question, selected_evidence, solver):

    evidence_text = "\n".join(
        sentence.text for sentence in selected_evidence
    )

    prompt = f"""
You are an evidence organizer.

Your task is to organize the provided evidence
into clear and understandable statements.

QUESTION:
{question}

SELECTED EVIDENCE:
{evidence_text}

Instructions:
1. Preserve the original facts.
2. Organize related information.
3. Do not introduce new information.
4. Do not answer the question.
5. Return only the organized evidence.
"""

    response = ollama.chat(
        model="tinyllama:latest",
        messages=[
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0}
    )

    recited_evidence = response.message.content

    # Send organized evidence to Solver
    answer = solver(question, recited_evidence)

    return {
        "route": "recite",
        "recited_evidence": recited_evidence,
        "answer": answer,
        "widen_attempts": 0
    }


# -----------------------------------------
# ROUTE 3: FULL DOCUMENT
# -----------------------------------------

def split_into_chunks(text, max_words=2500, overlap=150):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = min(start + max_words, len(words))

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


def full_document_route(question, full_document, solver):

    max_words = 2500

    document_words = full_document.split()

    # If document fits within the configured limit
    if len(document_words) <= max_words:

        answer = solver(question, full_document)

    else:

        # Divide document into smaller chunks
        chunks = split_into_chunks(
            full_document,
            max_words=max_words,
            overlap=150
        )

        partial_answers = []

        # Process each chunk
        for index, chunk in enumerate(chunks):

            print(f"Processing document chunk {index + 1}/{len(chunks)}")

            partial_answer = solver(question, chunk)

            partial_answers.append(partial_answer)

        # Combine partial answers
        combined_context = "\n".join(partial_answers)

        answer = solver(question, combined_context)

    return {
        "route": "full",
        "answer": answer,
        "widen_attempts": 0
    }


# -----------------------------------------
# ROUTE 4: MEDIUM CONFIDENCE EXPANSION
# -----------------------------------------

def handle_expansion(
    original_data,
    highlighter_widen,
    evaluate_gate,
    solver,
    full_document
):

    # Ask Highlighter for additional evidence ONCE
    expanded_data = highlighter_widen(original_data)

    # Recheck Confidence Gate
    new_confidence_result = evaluate_gate(expanded_data)

    new_confidence = new_confidence_result["confidence"]

    selected_evidence = expanded_data.selected_evidence

    question = expanded_data.question

    print("\nConfidence after expansion:", new_confidence)

    # If HIGH, use direct route
    if new_confidence == "high":

        result = direct_route(
            question,
            selected_evidence,
            solver
        )

    # If MEDIUM or LOW, use Recite-Then-Solve
    elif new_confidence in ["medium", "low"]:

        result = recite_route(
            question,
            selected_evidence,
            solver
        )

    # If VERY LOW, use full document
    elif new_confidence == "very_low":

        result = full_document_route(
            question, full_document, solver
        )

    else:
        raise ValueError("Invalid confidence level.")

    result["widen_attempts"] = 1
    result["final_confidence"] = new_confidence

    return result


# -----------------------------------------
# MAIN ROUTER
# -----------------------------------------

def route_request(
    confidence_result,
    question,
    selected_evidence,
    full_document,
    solver,
    original_data=None,
    highlighter_widen=None,
    evaluate_gate=None
):

    confidence = confidence_result["confidence"]


    # HIGH
    if confidence == "high":

        print("Route: DIRECT")

        return direct_route(
            question,
            selected_evidence,
            solver
        )

    # MEDIUM
    elif confidence == "medium":

        print("Route: EXPAND")

        if (
            highlighter_widen is None
            or evaluate_gate is None
            or original_data is None
        ):
            raise ValueError(
                "Original data, Highlighter widening "
                "and Gate evaluation functions are required."
            )

        return handle_expansion(
            original_data,
            highlighter_widen,
            evaluate_gate,
            solver,
            full_document
        )

    # LOW
    elif confidence == "low":

        print("Route: RECITE")

        return recite_route(
            question,
            selected_evidence,
            solver
        )

    # VERY LOW
    elif confidence == "very_low":

        print("Route: FULL")

        return full_document_route(
            question,
            full_document,
            solver
        )

    else:

        raise ValueError(
            f"Unknown confidence level: {confidence}"
        )