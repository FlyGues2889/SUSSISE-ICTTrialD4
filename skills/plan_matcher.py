LEVEL_ORDER = {"low": 0, "medium": 1, "high": 2}


def match_plans(all_plans: list, risk_level: str, target_area: str, duration_min: int, scene: str) -> list:
    scored = []
    for plan in all_plans:
        suitable = plan.get("suitable_level", "")
        if suitable and risk_level not in suitable:
            continue

        contraindication = plan.get("contraindication", "")
        if risk_level == "high" and contraindication:
            continue

        score = 0.0

        if plan["target_area"] == target_area:
            score += 0.4
        elif plan["target_area"] == "full":
            score += 0.2

        if plan["duration_min"] == duration_min:
            score += 0.3
        else:
            score += 0.3 * (1 - abs(plan["duration_min"] - duration_min) / 15)

        if plan["scene"] == scene:
            score += 0.2

        score += 0.1

        scored.append({**plan, "match_score": round(score, 2)})

    scored.sort(key=lambda x: -x["match_score"])
    return scored[:3]