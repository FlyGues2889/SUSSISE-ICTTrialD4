NECK_QUESTIONS = {
    "N1": {"dimension": "僵硬程度", "label": "最近一周颈部僵硬感出现的频率"},
    "N2": {"dimension": "活动受限", "label": "颈部疼痛是否影响转头看后方"},
    "N3": {"dimension": "疼痛频率", "label": "肩部是否有酸胀感，尤其是下午"},
    "N4": {"dimension": "姿势习惯", "label": "是否经常感到头前伸或圆肩"},
    "N5": {"dimension": "安全红线", "label": "颈部疼痛是否放射到手臂或手指"},
    "N6": {"dimension": "姿势习惯", "label": "久坐后是否需要用手支撑头部"},
    "N7": {"dimension": "僵硬程度", "label": "肩颈活动时是否有咔咔响声"},
    "N8": {"dimension": "疼痛频率", "label": "肩颈不适是否影响睡眠"},
}

BACK_QUESTIONS = {
    "B1": {"dimension": "疼痛频率", "label": "最近一周腰部酸痛感出现的频率"},
    "B2": {"dimension": "活动受限", "label": "弯腰时是否感到腰部受限"},
    "B3": {"dimension": "僵硬程度", "label": "久坐后背部是否有僵硬感"},
    "B4": {"dimension": "姿势习惯", "label": "是否经常感到弯腰驼背姿势"},
    "B5": {"dimension": "安全红线", "label": "腰背痛是否伴有下肢麻木或放射痛"},
    "B6": {"dimension": "活动受限", "label": "久站后是否感到腰部无力需要坐下"},
    "B7": {"dimension": "僵硬程度", "label": "腰部活动时是否有弹响或卡顿感"},
    "B8": {"dimension": "疼痛频率", "label": "腰背不适是否影响日常活动"},
}

RED_LINE_KEYS = {"N5", "B5"}

DIMENSION_LABELS = {
    "疼痛频率": "疼痛频率偏高",
    "僵硬程度": "僵硬感明显",
    "活动受限": "活动受限",
    "姿势习惯": "姿势习惯不良",
}


def assess_posture(area: str, answers: dict) -> dict:
    questions = NECK_QUESTIONS if area == "neck" else BACK_QUESTIONS

    total_score = sum(answers.values())
    red_line_hit = any(answers.get(k, 0) >= 1 for k in RED_LINE_KEYS if k in answers)

    if red_line_hit or total_score >= 13:
        risk_level = "high"
    elif total_score >= 6:
        risk_level = "medium"
    else:
        risk_level = "low"

    problem_dims = {}
    for qid, score in answers.items():
        if qid in questions and score >= 2:
            dim = questions[qid]["dimension"]
            problem_dims[dim] = problem_dims.get(dim, 0) + 1

    problem_points = []
    for dim, count in sorted(problem_dims.items(), key=lambda x: -x[1]):
        label = DIMENSION_LABELS.get(dim, dim)
        problem_points.append(label)

    if risk_level == "high":
        suggestion = "您的评估结果提示风险较高，建议前往骨科或康复科就诊检查。本工具暂不提供运动方案。"
    elif risk_level == "medium":
        suggestion = "建议每日进行针对性碎片化运动，注意纠正不良姿势，如持续不适请及时就医。"
    else:
        suggestion = "当前状况良好，建议保持每日预防性碎片化运动，维持肩颈腰背健康。"

    return {
        "risk_level": risk_level,
        "total_score": total_score,
        "problem_points": problem_points,
        "suggestion": suggestion,
        "red_line_hit": red_line_hit,
    }