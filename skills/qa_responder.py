def respond_qa(question: str, kb_items: list) -> dict:
    if not kb_items:
        return {"answer": "知识库暂未配置，请稍后再试。", "related_plans": [], "confidence": 0.0}

    question_lower = question.lower()
    scored = []

    for item in kb_items:
        keywords = item.get("keywords", "")
        kw_list = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

        matched = sum(1 for kw in kw_list if kw in question_lower)
        if not kw_list:
            score = 0.0
        else:
            score = matched / len(kw_list)

        for word in question_lower:
            if word in item.get("question", "").lower():
                score += 0.05

        scored.append((item, score))

    scored.sort(key=lambda x: -x[1])
    best, best_score = scored[0]

    if best_score < 0.1:
        return {
            "answer": "抱歉，暂时无法回答这个问题。建议您咨询专业医生或康复师。",
            "related_plans": [],
            "confidence": 0.0,
        }

    return {
        "answer": best["answer"],
        "related_plans": best.get("related_plans", []),
        "confidence": round(best_score, 2),
        "matched_question": best["question"],
    }