from modules.self_checker import check_evidence_sufficiency
from modules.input_handler import SentenceCandidate

question = "What are the limitations of the proposed method?"

selected_evidence = [
    SentenceCandidate(
        id=2,
        text="The proposed method reduces processing time.",
        position=2,
        score=0.84,
        selected=True
    ),
    SentenceCandidate(
        id=3,
        text="The proposed method has high computational cost.",
        position=3,
        score=0.91,
        selected=True
    )
]

result = check_evidence_sufficiency(
    question,
    selected_evidence
)

print(result)