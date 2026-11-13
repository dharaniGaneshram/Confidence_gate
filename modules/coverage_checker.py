import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Common English words to remove
STOPWORDS = {
    "what", "is", "are", "was", "were", "the", "a", "an",
    "of", "in", "on", "at", "to", "for", "from", "by",
    "with", "and", "or", "but", "how", "why", "when",
    "where", "which", "who", "does", "do", "did",
    "can", "could", "would", "should", "has", "have",
    "had", "it", "its", "this", "that", "these", "those",
    "their", "there", "they", "them", "about", "explain",
    "describe", "discuss", "tell", "me"
}


def extract_keywords(question):

    # Extract words and numbers
    tokens = re.findall(
        r"\b[A-Za-z]+(?:[-'][A-Za-z]+)*\b|\b\d+(?:\.\d+)?\b",
        question
    )

    keywords = []

    for token in tokens:

        # Keep numbers and remove common words
        if token.isdigit() or re.fullmatch(r"\d+(?:\.\d+)?", token):
            keywords.append(token)

        elif token.lower() not in STOPWORDS:
            keywords.append(token.lower())

    return list(dict.fromkeys(keywords))


def normalize_text(text):

    return re.sub(
        r"[^a-z0-9\s]",
        " ",
        text.lower()
    )


def exact_match(keyword, evidence_text):

    normalized_keyword = normalize_text(keyword)
    normalized_evidence = normalize_text(evidence_text)

    pattern = r"\b" + re.escape(normalized_keyword) + r"\b"

    return re.search(pattern, normalized_evidence) is not None


def check_coverage(
    question,
    selected_evidence,
    threshold=0.45
):

    # Extract important question words
    keywords = extract_keywords(question)

    # Get selected sentence texts
    evidence_sentences = [
        sentence.text for sentence in selected_evidence
    ]

    evidence_text = " ".join(evidence_sentences)

    matched_words = []
    missing_words = []
    matching_details = []

    # Create embeddings for selected evidence sentences
    if evidence_sentences:
        evidence_embeddings = model.encode(evidence_sentences)
    else:
        evidence_embeddings = None

    for keyword in keywords:

        # STEP 1: Exact matching
        if exact_match(keyword, evidence_text):

            matched_words.append(keyword)

            matching_details.append({
                "question_word": keyword,
                "matched_with": keyword,
                "match_type": "exact",
                "similarity_score": 1.0
            })

            continue

        # STEP 2: Semantic matching
        if evidence_embeddings is not None:

            keyword_embedding = model.encode([keyword])

            similarity_scores = cosine_similarity(
                keyword_embedding,
                evidence_embeddings
            )[0]

            best_index = int(np.argmax(similarity_scores))
            best_score = float(similarity_scores[best_index])

            if best_score >= threshold:

                matched_words.append(keyword)

                matching_details.append({
                    "question_word": keyword,
                    "matched_with": evidence_sentences[best_index],
                    "match_type": "semantic",
                    "similarity_score": round(best_score, 4)
                })

                continue

        # STEP 3: No match found
        missing_words.append(keyword)

        matching_details.append({
            "question_word": keyword,
            "matched_with": None,
            "match_type": "missing",
            "similarity_score": None
        })

    total_keywords = len(keywords)
    matched_count = len(matched_words)
    missing_count = len(missing_words)

    coverage_score = (
        matched_count / total_keywords
        if total_keywords > 0 else 0
    )

    return {
        "total_keywords": total_keywords,
        "matched_count": matched_count,
        "missing_count": missing_count,
        "coverage_score": round(coverage_score, 4),
        "matched_words": matched_words,
        "missing_words": missing_words,
        "matching_details": matching_details
    }