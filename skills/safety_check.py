def check_safety(risk_level: str, red_line_hit: bool, age: int | None = None, history: str | None = None) -> dict:
    if red_line_hit:
        return {
            "safe": False,
            "need_medical": True,
            "message": "您的评估结果出现放射性疼痛或下肢麻木等警示信号，建议尽快前往骨科或康复科就诊检查。",
        }

    if risk_level == "high":
        return {
            "safe": False,
            "need_medical": True,
            "message": "您的评估结果提示风险较高，建议前往骨科或康复科就诊。本工具暂不提供运动方案。",
        }

    if history and any(kw in history for kw in ["颈椎病", "腰椎间盘突出", "骨折", "术后", "急性"]):
        return {
            "safe": False,
            "need_medical": True,
            "message": "根据您提供的既往史，建议在医生指导下进行运动。本工具暂不提供运动方案。",
        }

    return {
        "safe": True,
        "need_medical": False,
        "message": "",
    }