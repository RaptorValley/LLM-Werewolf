import datetime

import init
import interact

provider: str = "OpenAI"
model_index: int = 0

# 新建12个玩家
players = [init.Player(id=i + 1, role=None) for i in range(12)]
interact.generate_log("已新建玩家")

# 调用方法为玩家分配身份
init.assign_roles(players, init.roles)
interact.generate_log("已为玩家分配身份")

# 狼人名册
werewolf_namelist = [player.id for player in players if player.role == "werewolf"]
interact.generate_log("狼人名册已生成")

# 神职名册
god_namelist = [
    player.id
    for player in players
    if player.role in ["seer", "witch", "hunter", "idiot"]
]
interact.generate_log("神职名册已生成")

# 村民名册
villager_namelist = [player.id for player in players if player.role == "villager"]
interact.generate_log("村民名册已生成")

# 女巫药水使用情况
witch_potion_used = {
    "antidote": False,  # 解药是否使用
    "poison": False,  # 毒药是否使用
}
interact.generate_log("女巫药水使用情况已生成")

# 游戏流程阶段列表
stages = [
    "night_start",  # 夜晚开始
    "werewolf_kill",  # 狼人行动
    "witch_action",  # 女巫行动
    "seer_check",  # 预言家行动
    "day_announce",  # 天亮公布结果
    "player_speech",  # 玩家发言阶段
    "vote",  # 投票阶段
]
interact.generate_log("游戏流程阶段列表已准备就绪")

# 上下文列表
context = [
    {
        "authority": "public",
        "serial": 0,
        "round": 0,
        "speaker": "narrator",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": "各位玩家大家好，欢迎来到狼人杀游戏。游戏即将开始，请大家做好准备。",
    },
]
interact.generate_log("上下文初始化完成")

# 动作执行列表
actions = [
    {
        "serial": 5,
        "round": 1,
        "operator": 8,
        "time": "2025-07-18 23:09:46",
        "target": 4,
    }
]

# 当前回合
current_round = 0
interact.generate_log(f"当前回合是第{current_round}回合")
