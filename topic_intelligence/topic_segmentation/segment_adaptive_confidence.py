from typing import List, Dict
import numpy as np


def compute_adaptive_threshold(similarities: List[float]) -> float:
    
    sims = np.array(similarities)

    if len(sims) < 2:
        return 0.0

    mean = sims.mean()
    std = sims.std()

    return max(mean - std, 0.0)


def score_boundaries(
    similarities: List[float],
    threshold: float
) -> List[Dict]:
    
    scored = []

    for idx, sim in enumerate(similarities):
        if sim < threshold:
            confidence = min(
                (threshold - sim) / threshold if threshold > 0 else 1.0,
                1.0
            )

            scored.append({
                "boundary_after_segment": idx,
                "similarity": float(sim),
                "confidence": round(confidence, 3)
            })

    return scored


def apply_confidence_to_topics(
    topics: List[Dict],
    boundary_scores: List[Dict]
) -> List[Dict]:
    
    score_map = {
        b["boundary_after_segment"]: b["confidence"]
        for b in boundary_scores
    }

    for topic in topics[:-1]:
        last_seg_id = topic["segments"][-1]["segment_id"]
        topic["boundary_confidence"] = score_map.get(last_seg_id, 0.0)

    topics[-1]["boundary_confidence"] = None
    return topics
