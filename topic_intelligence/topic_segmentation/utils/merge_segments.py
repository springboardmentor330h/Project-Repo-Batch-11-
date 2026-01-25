def merge_short_segments(segments, min_chars=120):
    merged = []
    buffer = None

    for seg in segments:
        if buffer is None:
            buffer = seg.copy()
            continue

        if len(buffer["translation"]) < min_chars:
            buffer["translation"] += " " + seg["translation"]
            buffer["end"] = seg["end"]
        else:
            merged.append(buffer)
            buffer = seg.copy()

    if buffer:
        merged.append(buffer)

    return merged
