# 体态评估：肩颈区与腰背区各 12 题，6 维度，加权总分判分
# 选项统一 4 档 0-3 分（无/偶尔/经常/持续）
# 题目权重 weight：姿势习惯题 0.8、常规题 1.0、红线/神经症状题 1.5
# 加权总分 = sum(score_i × weight_i)，四舍五入取整存 DB
# 满分 max_score = 3 × sum(weights) = 3 × 12.2 = 36.6
# 风险阈值：low < max×35%=12.81，medium < max×65%=23.79，high ≥ 23.79 或红线命中
# 红线题得分 ≥ 2（经常及以上）才触发就医，偶尔计入加权分但不强制就医
# 维度问题阈值 = 该维度满分 × 40%（超过即列为问题点，按维度加权得分降序输出）

NECK_QUESTIONS = {
    "N1": {"dimension": "僵硬程度", "weight": 1.0, "label": "最近一周颈部僵硬感出现的频率"},
    "N2": {"dimension": "活动受限", "weight": 1.0, "label": "颈部疼痛是否影响转头看后方"},
    "N3": {"dimension": "疼痛频率", "weight": 1.0, "label": "肩部是否有酸胀感，尤其是下午"},
    "N4": {"dimension": "姿势习惯", "weight": 0.8, "label": "是否经常感到头前伸或圆肩"},
    "N5": {"dimension": "神经症状", "weight": 1.5, "label": "颈部疼痛是否放射到手臂或手指"},
    "N6": {"dimension": "姿势习惯", "weight": 0.8, "label": "久坐后是否需要用手支撑头部"},
    "N7": {"dimension": "僵硬程度", "weight": 0.8, "label": "肩颈活动时是否有咔咔响声"},
    "N8": {"dimension": "功能影响", "weight": 1.0, "label": "肩颈不适是否影响睡眠"},
    "N9": {"dimension": "疼痛频率", "weight": 1.0, "label": "最近一周颈部疼痛是否持续存在"},
    "N10": {"dimension": "活动受限", "weight": 1.0, "label": "仰头或低头时是否感到受限"},
    "N11": {"dimension": "神经症状", "weight": 1.5, "label": "是否出现手部握力下降或持物不稳"},
    "N12": {"dimension": "功能影响", "weight": 0.8, "label": "久坐后是否需休息才能缓解肩颈疲劳"},
}

BACK_QUESTIONS = {
    "B1": {"dimension": "疼痛频率", "weight": 1.0, "label": "最近一周腰部酸痛感出现的频率"},
    "B2": {"dimension": "活动受限", "weight": 1.0, "label": "弯腰时是否感到腰部受限"},
    "B3": {"dimension": "僵硬程度", "weight": 1.0, "label": "久坐后背部是否有僵硬感"},
    "B4": {"dimension": "姿势习惯", "weight": 0.8, "label": "是否经常感到弯腰驼背姿势"},
    "B5": {"dimension": "神经症状", "weight": 1.5, "label": "腰背痛是否伴有下肢麻木或放射痛"},
    "B6": {"dimension": "活动受限", "weight": 1.0, "label": "久站后是否感到腰部无力需要坐下"},
    "B7": {"dimension": "僵硬程度", "weight": 0.8, "label": "腰部活动时是否有弹响或卡顿感"},
    "B8": {"dimension": "功能影响", "weight": 1.0, "label": "腰背不适是否影响日常活动"},
    "B9": {"dimension": "疼痛频率", "weight": 1.0, "label": "晨起时是否感到腰部疼痛"},
    "B10": {"dimension": "姿势习惯", "weight": 0.8, "label": "是否习惯久坐或坐姿不正"},
    "B11": {"dimension": "神经症状", "weight": 1.5, "label": "是否因腰背痛在夜间痛醒"},
    "B12": {"dimension": "功能影响", "weight": 0.8, "label": "久坐后腰背疼痛是否难以自行缓解"},
}

RED_LINE_KEYS = {"N5", "N11", "B5", "B11"}

DIMENSION_LABELS = {
    "疼痛频率": "疼痛频率偏高",
    "僵硬程度": "僵硬感明显",
    "活动受限": "活动受限",
    "姿势习惯": "姿势习惯不良",
    "神经症状": "神经症状警示",
    "功能影响": "功能影响明显",
}

MAX_SCORE = 36.6
LOW_THRESHOLD = MAX_SCORE * 0.35   # 12.81
HIGH_THRESHOLD = MAX_SCORE * 0.65  # 23.79
MEDIUM_SPLIT = (LOW_THRESHOLD + HIGH_THRESHOLD) / 2  # 18.3，中低/中高分界
DIM_PROBLEM_RATIO = 0.4


def assess_posture(area: str, answers: dict) -> dict:
    questions = NECK_QUESTIONS if area == "neck" else BACK_QUESTIONS

    weighted_total = 0.0
    for qid, score in answers.items():
        if qid in questions:
            weighted_total += score * questions[qid]["weight"]
    total_score = round(weighted_total)

    red_line_hit = any(answers.get(k, 0) >= 2 for k in RED_LINE_KEYS if k in answers)

    if red_line_hit or total_score >= HIGH_THRESHOLD:
        risk_grade = "high"
    elif total_score >= MEDIUM_SPLIT:
        risk_grade = "medium_high"
    elif total_score >= LOW_THRESHOLD:
        risk_grade = "medium_low"
    else:
        risk_grade = "low"
    risk_level = {"low": "low", "medium_low": "medium", "medium_high": "medium", "high": "high"}[risk_grade]

    dim_scores = {}
    dim_max = {}
    for qid, score in answers.items():
        if qid in questions:
            dim = questions[qid]["dimension"]
            w = questions[qid]["weight"]
            dim_scores[dim] = dim_scores.get(dim, 0.0) + score * w
            dim_max[dim] = dim_max.get(dim, 0.0) + 3 * w

    problem_points = []
    for dim, score in sorted(dim_scores.items(), key=lambda x: -x[1]):
        if dim_max.get(dim, 0) > 0 and score >= dim_max[dim] * DIM_PROBLEM_RATIO:
            problem_points.append(DIMENSION_LABELS.get(dim, dim))

    if risk_level == "high":
        suggestion = "您的评估结果提示风险较高，建议前往骨科或康复科就诊检查。本工具暂不提供运动方案。"
    elif risk_level == "medium":
        suggestion = "建议每日进行针对性碎片化运动，注意纠正不良姿势，如持续不适请及时就医。"
    else:
        suggestion = "当前状况良好，建议保持每日预防性碎片化运动，维持肩颈腰背健康。"

    return {
        "risk_level": risk_level,
        "risk_grade": risk_grade,
        "total_score": total_score,
        "problem_points": problem_points,
        "suggestion": suggestion,
        "red_line_hit": red_line_hit,
    }