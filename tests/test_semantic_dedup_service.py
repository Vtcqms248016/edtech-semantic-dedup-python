from src.semantic_dedup_service import decide_duplicate


def test_business_threshold_marks_near_duplicate() -> None:
    assert decide_duplicate(0.91) is True
    assert decide_duplicate(0.72) is False
