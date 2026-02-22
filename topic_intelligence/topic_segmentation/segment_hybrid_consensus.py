from typing import List, Dict, Set


def _extract_boundaries(topics: List[Dict]) -> Set[int]:
  
    boundaries = set()
    for topic in topics[:-1]:
        last_segment = topic["segments"][-1]
        boundaries.add(last_segment["segment_id"])
    return boundaries


def segment_hybrid_consensus(
    sentences: List[Dict],
    algo_outputs: Dict[str, List[Dict]],
    min_votes: int = 2
) -> List[Dict]:
    
    boundary_votes = {}

    for algo_name, topics in algo_outputs.items():
        boundaries = _extract_boundaries(topics)
        for b in boundaries:
            boundary_votes[b] = boundary_votes.get(b, 0) + 1

    final_boundaries = {
        b for b, votes in boundary_votes.items()
        if votes >= min_votes
    }

    topics = []
    topic_id = 0

    current_topic = {
        "topic_id": topic_id,
        "start": sentences[0]["start"],
        "end": sentences[0]["end"],
        "segments": [sentences[0]],
        "algorithm": "hybrid_consensus"
    }

    for i in range(1, len(sentences)):
        prev_id = sentences[i - 1]["segment_id"]

        if prev_id in final_boundaries:
            topics.append(current_topic)
            topic_id += 1
            current_topic = {
                "topic_id": topic_id,
                "start": sentences[i]["start"],
                "end": sentences[i]["end"],
                "segments": [sentences[i]],
                "algorithm": "hybrid_consensus"
            }
        else:
            current_topic["segments"].append(sentences[i])
            current_topic["end"] = sentences[i]["end"]

    topics.append(current_topic)
    return topics
