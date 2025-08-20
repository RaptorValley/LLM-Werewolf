import random
import datetime

# 模拟时间起点：stimulate time start
sts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


# 定义玩家类
class Player:
    def __init__(self, id, role):
        self.id = id  # 玩家编号
        self.role = role  # 身份
        self.is_alive = True  # 是否存活
        self.impressions = [
            {"content": "", "role": ""} for _ in range(12)
        ]  # 对其它玩家的印象
        self.recent_msg = []  # 最近的消息

    def reflect(self):
        # 反思自己在游戏中的表现
        pass


# 定义为玩家分配身份的函数
def assign_roles(players, roles):
    """
    为玩家随机分配身份。
    players: 玩家对象列表
    roles: 身份字符串列表（与玩家数量相同）
    """
    if len(players) != len(roles):
        raise ValueError("玩家数量与身份数量不一致")
    roles_copy = roles[:]  # 避免修改原列表
    random.shuffle(roles_copy)
    index = 1  # 玩家序号
    for player, role in zip(players, roles_copy):
        player.role = role
        player.id = index
        index += 1


# 英文身份列表（全部小写）
roles = [
    # werewolf 阵营
    "werewolf",
    "werewolf",
    "werewolf",
    "werewolf",
    # god 阵营
    "seer",
    "witch",
    "hunter",
    "idiot",
    # villager 阵营
    "villager",
    "villager",
    "villager",
    "villager",
]
