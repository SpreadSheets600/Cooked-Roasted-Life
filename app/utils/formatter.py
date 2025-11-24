def strip_empty(d: dict):
    return {k: v for k, v in d.items() if v}


def flatten_for_prompt(combined_dict: dict):
    lines = []
    for source, data in combined_dict.items():
        if source == "sources":
            continue
        if isinstance(data, dict):
            lines.append(f"[{source}]")
            for k, v in data.items():
                lines.append(f"{k}: {v}")
    return "\n".join(lines)
