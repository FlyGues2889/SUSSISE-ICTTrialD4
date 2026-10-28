import json
import os

AREAS = {"neck": "肩颈", "back": "腰背", "full": "全身"}
SCENES = {"desk": "办公桌前", "standing": "站立休息", "home": "居家"}
DURATIONS = [3, 5, 10, 15]

MOVEMENT_TEMPLATES = {
    ("neck", 3): [
        {"name": "颈部前屈后伸", "duration_sec": 30, "description": "缓慢前屈至下巴贴胸，再缓慢后伸，不过度仰头", "tips": "动作缓慢，感受颈部拉伸"},
        {"name": "颈部左右侧屈", "duration_sec": 30, "description": "耳朵向肩方向倾斜，不耸肩，左右各一次", "tips": "感受颈部侧面拉伸"},
        {"name": "肩部环绕", "duration_sec": 30, "description": "双肩同时向前环绕5圈，再向后环绕5圈", "tips": "幅度由小到大"},
        {"name": "肩胛骨收缩", "duration_sec": 30, "description": "双臂胸前交叉后展，肩胛骨向中间收缩", "tips": "感受肩胛骨靠拢"},
        {"name": "上背部伸展", "duration_sec": 30, "description": "双手扶桌，身体后仰，伸展上背部", "tips": "幅度适中"},
        {"name": "深呼吸放松", "duration_sec": 30, "description": "腹式呼吸5-8次，吸气4秒呼气6秒", "tips": "呼气比吸气长"},
    ],
    ("neck", 5): [
        {"name": "颈部前屈后伸", "duration_sec": 40, "description": "缓慢前屈至下巴贴胸，再缓慢后伸", "tips": "动作缓慢"},
        {"name": "颈部左右侧屈", "duration_sec": 40, "description": "耳朵向肩方向倾斜，左右各保持5秒", "tips": "不耸肩"},
        {"name": "颈部旋转", "duration_sec": 40, "description": "缓慢顺时针旋转5圈，再逆时针5圈", "tips": "幅度由小到大"},
        {"name": "肩部环绕", "duration_sec": 40, "description": "双肩向前环绕8圈，再向后8圈", "tips": "感受肩关节活动"},
        {"name": "肩胛骨收缩", "duration_sec": 40, "description": "双臂胸前交叉后展，保持5秒重复8次", "tips": "感受肩胛骨靠拢"},
        {"name": "上背部伸展", "duration_sec": 40, "description": "双手扶桌，身体后仰伸展", "tips": "幅度适中"},
        {"name": "胸部开合", "duration_sec": 40, "description": "双手背后交叉，挺胸抬头保持5秒重复8次", "tips": "改善圆肩"},
    ],
    ("back", 3): [
        {"name": "坐姿猫牛式", "duration_sec": 30, "description": "坐姿交替弓背和挺背，配合呼吸", "tips": "动作跟随呼吸节奏"},
        {"name": "坐姿扭转", "duration_sec": 30, "description": "右手扶左膝，身体向左扭转，左右各一次", "tips": "感受腰部扭转"},
        {"name": "腰部前屈", "duration_sec": 30, "description": "坐姿缓慢前屈，双手触地，保持10秒", "tips": "感受腰背拉伸"},
        {"name": "骨盆前后倾", "duration_sec": 30, "description": "坐姿交替骨盆前倾和后倾，各保持3秒", "tips": "激活核心肌群"},
        {"name": "侧腰拉伸", "duration_sec": 30, "description": "右手举过头顶，身体向左侧弯，左右各一次", "tips": "感受侧腰拉伸"},
        {"name": "深呼吸放松", "duration_sec": 30, "description": "腹式呼吸5-8次", "tips": "放松腰背"},
    ],
    ("back", 5): [
        {"name": "坐姿猫牛式", "duration_sec": 40, "description": "坐姿交替弓背和挺背，配合呼吸10次", "tips": "动作跟随呼吸"},
        {"name": "坐姿扭转", "duration_sec": 40, "description": "右手扶左膝扭转保持10秒，左右各一次", "tips": "深度扭转"},
        {"name": "腰部前屈后伸", "duration_sec": 40, "description": "坐姿前屈双手触地保持10秒，再后伸", "tips": "幅度适中"},
        {"name": "骨盆前后倾", "duration_sec": 40, "description": "坐姿骨盆前倾后倾各保持5秒，重复8次", "tips": "激活核心"},
        {"name": "侧腰拉伸", "duration_sec": 40, "description": "单手举过头侧弯保持10秒，左右各一次", "tips": "深度拉伸"},
        {"name": "臀桥", "duration_sec": 40, "description": "坐姿改为仰卧，抬臀保持3秒重复10次", "tips": "激活臀部"},
        {"name": "婴儿式放松", "duration_sec": 40, "description": "跪姿前趴，双手前伸，臀部坐脚跟", "tips": "放松腰背"},
    ],
    ("full", 3): [
        {"name": "颈部环绕", "duration_sec": 25, "description": "缓慢顺时针再逆时针各3圈", "tips": "动作缓慢"},
        {"name": "肩部环绕", "duration_sec": 25, "description": "双肩前后各环绕5圈", "tips": "幅度由小到大"},
        {"name": "坐姿扭转", "duration_sec": 25, "description": "身体左右扭转各保持5秒", "tips": "感受脊柱扭转"},
        {"name": "站姿伸展", "duration_sec": 25, "description": "起身双手上举伸展全身", "tips": "感受全身拉伸"},
        {"name": "深呼吸", "duration_sec": 25, "description": "腹式呼吸5次", "tips": "放松身心"},
    ],
    ("neck", 10): [
        {"name": "颈部全方位活动", "duration_sec": 60, "description": "前屈后伸、左右侧屈、旋转各10次", "tips": "全面活动颈椎"},
        {"name": "肩部深度环绕", "duration_sec": 60, "description": "双肩大幅环绕前后各10圈", "tips": "活动肩关节"},
        {"name": "肩胛骨强化", "duration_sec": 60, "description": "肩胛骨收缩保持10秒重复10次", "tips": "强化中斜方肌"},
        {"name": "胸部开合", "duration_sec": 60, "description": "双手背后交叉挺胸保持10秒重复8次", "tips": "改善圆肩"},
        {"name": "上背部伸展", "duration_sec": 60, "description": "双手扶桌身体后仰保持15秒", "tips": "深度伸展"},
        {"name": "颈部等长收缩", "duration_sec": 60, "description": "手抵额头互推保持5秒，各方向重复5次", "tips": "强化颈部肌群"},
        {"name": "深呼吸放松", "duration_sec": 60, "description": "腹式呼吸10次", "tips": "放松收尾"},
    ],
    ("back", 10): [
        {"name": "猫牛式", "duration_sec": 60, "description": "四点跪姿交替弓背挺背15次", "tips": "灵活脊柱"},
        {"name": "坐姿扭转", "duration_sec": 60, "description": "深扭转左右各保持15秒", "tips": "深度放松"},
        {"name": "臀桥", "duration_sec": 60, "description": "仰卧抬臀保持3秒重复15次", "tips": "强化臀腰"},
        {"name": "侧腰拉伸", "duration_sec": 60, "description": "侧弯保持15秒左右各2次", "tips": "拉伸侧腰"},
        {"name": "婴儿式", "duration_sec": 60, "description": "跪姿前趴保持30秒", "tips": "放松腰背"},
        {"name": "鸟狗式", "duration_sec": 60, "description": "对侧手脚伸展保持3秒交替10次", "tips": "核心稳定"},
        {"name": "深呼吸", "duration_sec": 60, "description": "腹式呼吸10次", "tips": "放松收尾"},
    ],
    ("full", 5): [
        {"name": "颈部活动", "duration_sec": 40, "description": "前屈后伸侧屈各5次", "tips": "缓慢活动"},
        {"name": "肩部环绕", "duration_sec": 40, "description": "前后各8圈", "tips": "活动肩关节"},
        {"name": "腰部扭转", "duration_sec": 40, "description": "左右扭转各保持8秒", "tips": "灵活脊柱"},
        {"name": "全身伸展", "duration_sec": 40, "description": "双手上举伸展保持10秒", "tips": "全身拉伸"},
        {"name": "深呼吸", "duration_sec": 40, "description": "腹式呼吸8次", "tips": "放松身心"},
    ],
    ("full", 10): [
        {"name": "全身关节活动", "duration_sec": 60, "description": "颈肩腰膝踝依次活动", "tips": "逐关节活动"},
        {"name": "猫牛式", "duration_sec": 60, "description": "交替弓背挺背15次", "tips": "灵活脊柱"},
        {"name": "臀桥", "duration_sec": 60, "description": "抬臀保持3秒重复12次", "tips": "强化臀腰"},
        {"name": "站姿前屈", "duration_sec": 60, "description": "双手触地保持15秒", "tips": "拉伸后链"},
        {"name": "侧腰拉伸", "duration_sec": 60, "description": "侧弯保持10秒左右各2次", "tips": "拉伸侧腰"},
        {"name": "婴儿式放松", "duration_sec": 60, "description": "跪姿前趴保持20秒", "tips": "放松全身"},
        {"name": "深呼吸", "duration_sec": 60, "description": "腹式呼吸10次", "tips": "收尾放松"},
    ],
    ("neck", 15): [
        {"name": "颈部全方位热身", "duration_sec": 90, "description": "各方向缓慢活动各10次", "tips": "充分热身"},
        {"name": "肩部深度环绕", "duration_sec": 90, "description": "大幅环绕前后各15圈", "tips": "活动肩关节"},
        {"name": "肩胛骨强化", "duration_sec": 90, "description": "收缩保持10秒重复12次", "tips": "强化中斜方肌"},
        {"name": "胸部开合", "duration_sec": 90, "description": "挺胸保持10秒重复10次", "tips": "改善圆肩"},
        {"name": "颈部等长收缩", "duration_sec": 90, "description": "各方向互推保持5秒重复8次", "tips": "强化颈部"},
        {"name": "上背部伸展", "duration_sec": 90, "description": "扶桌后仰保持20秒", "tips": "深度伸展"},
        {"name": "靠墙天使", "duration_sec": 90, "description": "靠墙双臂滑动10次", "tips": "纠正姿势"},
        {"name": "深呼吸放松", "duration_sec": 90, "description": "腹式呼吸15次", "tips": "放松收尾"},
    ],
    ("back", 15): [
        {"name": "猫牛式热身", "duration_sec": 90, "description": "交替弓背挺背20次", "tips": "充分热身"},
        {"name": "臀桥", "duration_sec": 90, "description": "抬臀保持5秒重复15次", "tips": "强化臀腰"},
        {"name": "鸟狗式", "duration_sec": 90, "description": "对侧伸展保持5秒交替12次", "tips": "核心稳定"},
        {"name": "死虫式", "duration_sec": 90, "description": "仰卧对侧手脚伸展保持3秒重复10次", "tips": "核心强化"},
        {"name": "坐姿扭转", "duration_sec": 90, "description": "深扭转左右各保持15秒", "tips": "深度放松"},
        {"name": "侧腰拉伸", "duration_sec": 90, "description": "侧弯保持15秒左右各3次", "tips": "深度拉伸"},
        {"name": "婴儿式", "duration_sec": 90, "description": "保持30秒", "tips": "放松腰背"},
        {"name": "深呼吸", "duration_sec": 90, "description": "腹式呼吸15次", "tips": "收尾放松"},
    ],
    ("full", 15): [
        {"name": "全身关节热身", "duration_sec": 90, "description": "颈肩腰膝踝依次活动", "tips": "充分热身"},
        {"name": "猫牛式", "duration_sec": 90, "description": "交替弓背挺背15次", "tips": "灵活脊柱"},
        {"name": "臀桥", "duration_sec": 90, "description": "保持5秒重复15次", "tips": "强化臀腰"},
        {"name": "鸟狗式", "duration_sec": 90, "description": "对侧伸展保持5秒交替10次", "tips": "核心稳定"},
        {"name": "站姿前屈", "duration_sec": 90, "description": "触地保持20秒", "tips": "拉伸后链"},
        {"name": "侧腰拉伸", "duration_sec": 90, "description": "侧弯保持15秒左右各2次", "tips": "拉伸侧腰"},
        {"name": "婴儿式", "duration_sec": 90, "description": "保持30秒", "tips": "放松全身"},
        {"name": "深呼吸", "duration_sec": 90, "description": "腹式呼吸15次", "tips": "收尾放松"},
    ],
}

CONTRAINDICATIONS = {
    "neck": "颈椎病急性期、肩袖损伤禁做颈部环绕；放射性疼痛禁做",
    "back": "腰椎间盘突出急性期禁做前屈；下肢放射痛禁做",
    "full": "急性疼痛期、术后未满3个月禁做",
}


def generate_plans():
    plans = []
    plan_id = 1
    for area in ["neck", "back", "full"]:
        for duration in DURATIONS:
            for scene in ["desk", "standing", "home"]:
                key = (area, duration)
                if key not in MOVEMENT_TEMPLATES:
                    continue
                movements = MOVEMENT_TEMPLATES[key]
                scene_label = SCENES[scene]
                area_label = AREAS[area]
                name = f"{scene_label}{duration}分钟{area_label}运动"

                plans.append({
                    "plan_id": plan_id,
                    "name": name,
                    "duration_min": duration,
                    "target_area": area,
                    "scene": scene,
                    "movements": movements,
                    "suitable_level": "low,medium" if area != "full" else "low,medium,high",
                    "contraindication": CONTRAINDICATIONS[area],
                    "description": f"针对{area_label}的{duration}分钟碎片化运动方案，适合{scene_label}场景",
                })
                plan_id += 1
    return plans


def generate_sql(plans):
    lines = ["-- 运动方案库种子数据", f"-- 共 {len(plans)} 个方案", ""]
    for p in plans:
        movements_json = json.dumps(p["movements"], ensure_ascii=False).replace("'", "''")
        suitable = p["suitable_level"].replace("'", "''")
        contra = p["contraindication"].replace("'", "''")
        desc = p["description"].replace("'", "''")
        name = p["name"].replace("'", "''")
        lines.append(
            f"INSERT INTO exercise_plan (name, duration_min, target_area, scene, movements, suitable_level, contraindication, description) "
            f"VALUES ('{name}', {p['duration_min']}, '{p['target_area']}', '{p['scene']}', "
            f"'{movements_json}', '{suitable}', '{contra}', '{desc}');"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    plans = generate_plans()
    sql = generate_sql(plans)
    output_path = os.path.join(os.path.dirname(__file__), "..", "project", "backend", "db", "seed_plans.sql")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"已生成 {len(plans)} 个方案到 {output_path}")