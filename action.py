import call
import config
import interact

import datetime


def werewolf_action():
    """
    狼人行动逻辑。
    这里可以实现狼人讨论、投票杀人等逻辑。
    """
    interact.generate_action("狼人活动环节已开始")
    temp_recent_msg = []  # 存储最近的消息
    # 狼人活动上下文
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": "现在是狼人活动时间。场上的四名狼人拥有1轮讨论机会，每轮讨论中每名玩家仅被允许发言一次。发言字数应在200-400字之间。讨论结束后，由狼人投票决定杀死一名玩家。请注意，狼人**必须**杀人。",
        }
    )
    temp_recent_msg.append(
        {
            "authority": config.werewolf_namelist,
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"{config.werewolf_namelist}属于狼人阵营。",
        }
    )
    interact.generate_action("狼人阵营名册已向狼人广播")
    interact.generate_action(f"{config.werewolf_namelist}系狼人阵营名册")

    # 狼人讨论
    interact.generate_action("狼人讨论开始")
    for i in range(1):  # 1轮讨论
        for wid in config.werewolf_namelist:
            # 修正索引，wid为玩家id，config.players索引应为wid-1
            if not config.players[wid - 1].is_alive:
                continue
            instruction = {
                "authority": config.werewolf_namelist,
                "serial": len(config.context),
                "round": config.context[-1]["round"],
                "speaker": "narrator",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": f"请{wid}号狼人玩家开始发言。",
            }
            temp_recent_msg.append(instruction)  # 将指令添加到上下文
            config.players[wid - 1].recent_msg = temp_recent_msg
            text = call.complete_caller(wid, instruction)  # 获取回复
            interact.generate_action(f"已向{wid}号狼人请求响应")
            config.players[wid - 1].recent_msg.append(
                {
                    "authority": config.werewolf_namelist,
                    "serial": len(config.context),
                    "round": config.context[-1]["round"],
                    "speaker": wid,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": text,
                }
            )
            temp_recent_msg = config.players[wid - 1].recent_msg

    config.context.extend(temp_recent_msg)  # 将最近消息附加到上下文
    interact.printer(context=config.context)  # 打印上下文
    interact.generate_action("已将狼人讨论内容打印在屏幕上")

    # 狼人投票
    interact.generate_action("狼人投票开始")
    vote_result = []
    for wid in config.werewolf_namelist:
        if not config.players[wid - 1].is_alive:
            continue
        instruction = {
            "authority": wid,
            "serial": len(config.context),
            "round": config.context[-1]["round"],
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"{wid}号玩家，请投票杀死一名玩家。",
        }
        interact.generate_action(f"已向{wid}号狼人请求响应")
        vote_target = call.complete_caller(wid, instruction, "target")  # 获取投票目标
        config.context.append(
            {
                "authority": wid,
                "serial": len(config.context),
                "round": config.context[-1]["round"],
                "speaker": "narrator",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": f"{wid}号狼人投给了{vote_target}号玩家。",
            }
        )
        interact.generate_action(f"{wid}号狼人投给了{vote_target}号玩家。")
        vote_result.append(vote_target)
        interact.printer(context=config.context)
    # 统计投票结果
    if not vote_result:
        return None
    if vote_result == [None, None, None, None]:
        return None
    index_killed_player = max(set(vote_result), key=vote_result.count)
    config.players[index_killed_player - 1].is_alive = False
    interact.generate_action(f"{vote_result}号玩家被狼人淘汰出局")
    return index_killed_player


def witch_action(dead):
    interact.generate_action("女巫行动开始")
    """
    女巫行动逻辑。
    这里可以实现女巫使用解药和毒药的逻辑。
    |返回值|含义|
    |:---:|:---:|
    |-1|女巫使用了解药，且成功救活了玩家|
    |0|女巫没有使用解药或毒药|
    |正整数|女巫使用了毒药，且成功杀死了玩家|
    |-3|女巫使用了解药，但失败了|
    |-2|女巫使用了毒药，但失败了|
    """
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": "现在是女巫活动时间。女巫可以选择使用解药救活该玩家，或使用毒药杀死一名玩家。请注意，女巫只能使用一次解药和一次毒药。现在，请您先给出解药的使用情况。当然，您也可以不使用。",
        }
    )
    for p in config.players:
        if p.role == "witch" and p.is_alive:
            # 解药
            if not config.witch_potion_used["antidote"]:
                interact.generate_log("询问女巫是否使用解药")
                instruction = {
                    "content": f'昨晚{dead}号玩家死亡，您是否使用解药？如是，请返回含"target"字段的json文本，内容为您要施救的对象。'
                }
                index_witch_action = call.complete_caller(p.id, instruction, "target")
                if index_witch_action is not None:
                    config.context.append(
                        {
                            "authority": p.id,
                            "serial": len(config.context),
                            "round": config.context[-1]["round"],
                            "speaker": "narrator",
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": f"您选择对{index_witch_action}号玩家使用解药。",
                        }
                    )
                    config.witch_potion_used["antidote"] = True
                    config.players[index_witch_action - 1].is_alive = True
                    interact.generate_action("女巫使用了解药")
                    interact.printer(context=config.context)
                    if dead == index_witch_action:
                        interact.generate_action("女巫行动结束")
                        return -1
                    else:
                        interact.generate_action("女巫行动结束")
                        return -3
                else:
                    config.context.append(
                        {
                            "authority": p.id,
                            "serial": len(config.context),
                            "round": config.context[-1]["round"],
                            "speaker": "narrator",
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": "您选择不使用解药。",
                        }
                    )
                    interact.generate_action("女巫未使用解药")
                    interact.printer(context=config.context)

            # 毒药
            if not config.witch_potion_used["poison"]:
                interact.generate_action("询问女巫是否使用毒药")
                instruction = {
                    "content": '您是否要使用毒药？如是，请返回含"target"字段的json格式，内容为您要施加毒药的玩家id。'
                }
                index_witch_action = call.complete_caller(p.id, instruction, "target")
                if index_witch_action is not None:
                    config.context.append(
                        {
                            "authority": p.id,
                            "serial": len(config.context),
                            "round": config.context[-1]["round"],
                            "speaker": "narrator",
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": f"您选择对{index_witch_action}号玩家使用毒药。",
                        }
                    )
                    interact.generate_action(
                        f"女巫选择对{index_witch_action}号玩家使用毒药"
                    )
                    config.witch_potion_used["poison"] = True
                    if config.players[index_witch_action - 1].is_alive:
                        config.players[index_witch_action - 1].is_alive = False
                        interact.printer(context=config.context)
                        interact.generate_action("女巫行动结束")
                        return index_witch_action - 1
                    else:
                        interact.generate_action("女巫行动结束")
                        return -2
                else:
                    config.context.append(
                        {
                            "authority": p.id,
                            "serial": len(config.context),
                            "round": config.context[-1]["round"],
                            "speaker": "narrator",
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": "您选择不使用毒药。",
                        }
                    )
                    interact.generate_action("女巫未使用毒药")
                    interact.printer(context=config.context)
                    interact.generate_action("女巫行动结束")
                    return 0


def seer_check():
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": "现在是预言家活动时间。请预言家选择一名玩家进行查验。",
        }
    )
    interact.generate_action("预言家活动环节已开始")
    for p in config.players:
        if p.role == "seer" and p.is_alive:
            instruction = {
                "content": '请返回一个含"target"的json文本，以指定您要查验的对象。'
            }
            index_seered_target = call.complete_caller(p.id, instruction, "target")
            if index_seered_target is not None:
                if config.players[index_seered_target - 1].role == "werewolf":
                    config.context.append(
                        {
                            "authority": p.id,
                            "serial": len(config.context),
                            "round": config.context[-1]["round"],
                            "speaker": "narrator",
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": f"您查验的玩家是{index_seered_target}号玩家，他的身份是狼人。",
                        }
                    )
                    interact.generate_action(
                        f"{p.id}号预言家查验了{index_seered_target}号玩家，身份是狼人"
                    )
                else:
                    config.context.append(
                        {
                            "authority": p.id,
                            "serial": len(config.context),
                            "round": config.context[-1]["round"],
                            "speaker": "narrator",
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": f"您查验的玩家是{index_seered_target}号玩家，他的身份不是狼人。",
                        }
                    )
                    interact.generate_action(
                        f"{p.id}号预言家查验了{index_seered_target}号玩家，身份不是狼人"
                    )
            else:
                config.context.append(
                    {
                        "authority": p.id,
                        "serial": len(config.context),
                        "round": config.context[-1]["round"],
                        "speaker": "narrator",
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "content": "您选择不查验任何玩家。",
                    }
                )
                interact.generate_action(f"{p.id}号预言家未查验任何玩家")
            interact.printer(context=config.context)


def hunter_action(pid):
    # 猎人遗言
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": "{}号玩家是猎人，他可以选择开枪杀死一名玩家。".format(pid),
        }
    )
    instruction = {
        "content": '您昨夜被狼人杀害。请用含"content"字段的json格式发表遗言。'
    }
    text = call.complete_caller(pid, instruction)
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": pid,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": text,
        }
    )
    interact.generate_action(f"{pid}号猎人正在发表遗言")
    # 猎人开枪
    instruction = {"content": '现在请用含"target"字段的json格式指定您要带走的对象。'}
    hunter_killed = call.complete_caller(pid, instruction, "target")
    if hunter_killed is not None:
        config.players[hunter_killed - 1].is_alive = False
        config.context.append(
            {
                "authority": "public",
                "serial": len(config.context),
                "round": config.current_round,
                "speaker": "narrator",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": "{}号玩家被猎人开枪杀死。".format(hunter_killed),
            }
        )
        interact.generate_action(f"{pid}号猎人开枪杀死了{hunter_killed}号玩家。")
    else:
        config.context.append(
            {
                "authority": "public",
                "serial": len(config.context),
                "round": config.current_round,
                "speaker": "narrator",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": f"{pid}号猎人没有选择开枪。",
            }
        )
        interact.generate_action(f"{pid}号猎人未开枪")
    interact.printer(context=config.context)


def final_speech(p):
    """
    玩家遗言
    """
    instruction = {
        "content": '您昨夜被狼人杀害。请用含"content"字段的json格式发表遗言。'
    }
    text = call.complete_caller(p.id, instruction)
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": p.id,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": text,
        }
    )
    interact.generate_action(f"{p.id}号玩家正在发表遗言")


def public_speech():
    """
    公共发言逻辑。
    这里可以实现公共发言的逻辑。
    """
    interact.generate_action("公共发言环节已开始")
    temp_recent_saving = []  # 新建空的最近消息列表（公用）
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": "现在是玩家发言时间。请所有存活的玩家依次发言。",
        }
    )
    instruction = {
        "content": '请与其他所有玩家进行讨论。将您的发言内容包含在json格式的"content"字段中。'
    }
    for p in config.players:
        if p.is_alive:
            if p.role == "werewolf":
                p.recent_msg.extend(
                    temp_recent_saving
                )  # 将玩家自己的最近消息列表与公共列表同步
            else:
                p.recent_msg = temp_recent_saving
            text = call.complete_caller(p.id, instruction)
            temp_recent_saving.append(
                {
                    "authority": "public",
                    "serial": len(config.context),
                    "round": config.context[-1]["round"],
                    "speaker": p.id,
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": text,
                }
            )  # 将玩家发言添加到它自己的消息列表中
            interact.generate_action(f"{p.id}号玩家正在发言")
            p.recent_msg = temp_recent_saving  # 同步公用消息列表
    config.context.extend(temp_recent_saving)
    interact.printer(context=config.context)
    for p in config.players:
        if p.is_alive:
            p.recent_msg = temp_recent_saving  # 更新每名玩家的最近消息列表以供后续环节


def generate_impressions():
    config.context.append(
        {
            "authority": None,
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": "玩家们正在生成对其他人的印象。",
        }
    )
    interact.printer(context=config.context)
    player_count = len(config.players)
    for p in config.players:
        if p.is_alive:
            # 保证 impressions 长度足够
            if len(p.impressions) < player_count:
                p.impressions += [
                    {"content": "", "role": ""}
                    for _ in range(player_count - len(p.impressions))
                ]
            for p0 in config.players:
                if p0.is_alive:
                    config.context.append(
                        {
                            "authority": None,
                            "serial": len(config.context),
                            "round": config.current_round,
                            "speaker": p.id,
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": f"{p.id}号玩家正在更新对{p0.id}号玩家的印象。",
                        }
                    )
                    interact.printer(context=config.context)
                    p.recent_msg.append(
                        {
                            "instruction": f'请更新您对每名玩家的印象。现在，让我们来谈谈你对{p0.id}号玩家的印象。将您对他的印象放在json格式的"content"字段当中，无需涉及"role"字段。**不超过15个字**'
                        }
                    )
                    p.impressions[p0.id - 1]["content"] = call.safe_caller(
                        p.recent_msg
                    )  # 获取印象
                    p.recent_msg.append(
                        {
                            "instruction": f'现在，让我们来谈谈你对{p0.id}号玩家的角色的看法。将您对他的角色的猜测放在json格式的"role"字段当中，无需涉及"content"字段。'
                        }
                    )
                    p.impressions[p0.id - 1]["role"] = call.safe_caller(
                        p.recent_msg, "role"
                    )  # 获取印象


def public_vote(context):
    """
    公共投票逻辑。
    这里可以实现公共投票的逻辑。
    """
    interact.generate_action("公共投票环节已开始")
    config.context.append(
        {
            "authority": "public",
            "serial": len(config.context),
            "round": config.current_round,
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": '现在是投票阶段。您在投票时，应使JSON格式包含"target"内容。请所有存活的玩家投票决定杀死一名玩家。',
        }
    )
    vote_list = []
    for p in config.players:
        if p.is_alive:
            instruction = {
                "content": '请投票选择要杀死的玩家。将您的选择放在json格式的"target"字段中。'
            }
            vote_target = call.complete_caller(p.id, instruction, "target")
            vote_list.append(vote_target)
            interact.generate_action(f"{p.id}号玩家投给了{vote_target}号玩家")
    if not vote_list:
        interact.generate_action("无人被投票出局")
        return None
    index_killed_player = max(set(vote_list), key=vote_list.count)
    if not index_killed_player:
        interact.generate_action("无人被投票出局")
        return None
    config.players[index_killed_player - 1].is_alive = False
    context.append(
        {
            "authority": "public",
            "serial": len(context),
            "round": context[-1]["round"],
            "speaker": "narrator",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"投票结果：{index_killed_player}号玩家被投票杀死。",
        }
    )
    interact.generate_action(f"{index_killed_player}号玩家被投票杀死")
    interact.printer(context=context)
    return index_killed_player


def is_game_over():
    """
    判断游戏是否结束。
    返回值0：游戏继续
    返回值1：好人胜利
    返回值-1：狼人胜利
    """
    werewolf_all_dead = True
    god_all_dead = True
    villager_all_dead = True
    # 判断狼人是否死光
    for p in config.werewolf_namelist:
        if config.players[p - 1].is_alive:
            werewolf_all_dead = False
            break

    # 判断神职是否死光
    for p in config.god_namelist:
        if config.players[p - 1].is_alive:
            god_all_dead = False
            break

    # 判断村民是否死光
    for p in config.villager_namelist:
        if config.players[p - 1].is_alive:
            villager_all_dead = False
            break

    if werewolf_all_dead:
        return 1
    elif god_all_dead and villager_all_dead:
        return -1
    else:
        return 0


def game_over(result):
    match result:
        case 1:
            config.context.append(
                {
                    "authority": "public",
                    "serial": len(config.context),
                    "round": config.context[-1]["round"],
                    "speaker": "narrator",
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": "好人胜利！游戏结束。",
                }
            )
            interact.generate_action("好人胜利！游戏结束。")
            return True
        case -1:
            config.context.append(
                {
                    "authority": "public",
                    "serial": len(config.context),
                    "round": config.context[-1]["round"],
                    "speaker": "narrator",
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "content": "狼人胜利！游戏结束。",
                }
            )
            interact.generate_action("狼人胜利！游戏结束。")
            return True
        case _:
            return False


def game_loop():
    while True:
        # for i in range(1):
        for stage in config.stages:
            if stage == "night_start":
                # 夜晚开始逻辑
                config.current_round += 1
                alive_players = [p.id for p in config.players if p.is_alive]
                config.context.append(
                    {
                        "authority": "public",
                        "serial": len(config.context),
                        "round": config.current_round,
                        "speaker": "narrator",
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "content": "第{}夜开始。目前场上存活的玩家有：{}。".format(
                            config.current_round, alive_players
                        ),
                    }
                )
                interact.printer(context=config.context)
            elif stage == "werewolf_kill":
                werewolf_killed = werewolf_action()  # 调用狼人行动逻辑
            elif stage == "seer_check":
                # 预言家查验逻辑
                seer_check()  # 调用预言家查验逻辑
            elif stage == "witch_action":
                # 女巫操作逻辑
                witch_result = witch_action(werewolf_killed)
            elif stage == "day_announce":
                # 公布夜间结果
                if werewolf_killed is not None:
                    match witch_result:
                        case -1:
                            config.context.append(
                                {
                                    "authority": "public",
                                    "serial": len(config.context),
                                    "round": config.current_round,
                                    "speaker": "narrator",
                                    "time": datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "content": "天亮了，昨晚是平安夜。",
                                }
                            )
                        case -3:
                            config.context.append(
                                {
                                    "authority": "public",
                                    "serial": len(config.context),
                                    "round": config.current_round,
                                    "speaker": "narrator",
                                    "time": datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "content": "天亮了，昨晚{}号玩家死亡。".format(
                                        werewolf_killed
                                    ),
                                }
                            )
                            if config.players[werewolf_killed - 1].role == "hunter":
                                hunter_action(werewolf_killed)
                            else:
                                final_speech(config.players[werewolf_killed - 1])

                        case -2:
                            config.context.append(
                                {
                                    "authority": "public",
                                    "serial": len(config.context),
                                    "round": config.current_round,
                                    "speaker": "narrator",
                                    "time": datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "content": "天亮了，昨晚{}号玩家死亡。".format(
                                        werewolf_killed
                                    ),
                                }
                            )
                            if config.players[werewolf_killed - 1].role == "hunter":
                                hunter_action(werewolf_killed)
                            else:
                                final_speech(config.players[werewolf_killed - 1])
                        case 0:
                            config.context.append(
                                {
                                    "authority": "public",
                                    "serial": len(config.context),
                                    "round": config.current_round,
                                    "speaker": "narrator",
                                    "time": datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "content": "天亮了，昨晚{}号玩家死亡。".format(
                                        werewolf_killed
                                    ),
                                }
                            )
                            if config.players[werewolf_killed - 1].role == "hunter":
                                hunter_action(werewolf_killed)
                            else:
                                final_speech(config.players[werewolf_killed - 1])
                        case _:
                            config.context.append(
                                {
                                    "authority": "public",
                                    "serial": len(config.context),
                                    "round": config.current_round,
                                    "speaker": "narrator",
                                    "time": datetime.datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    "content": "天亮了，昨晚{}号和{}号玩家死亡。".format(
                                        werewolf_killed, witch_result
                                    ),
                                }
                            )
                            if config.players[werewolf_killed - 1].role == "hunter":
                                hunter_action(werewolf_killed)
                            else:
                                final_speech(config.players[werewolf_killed - 1])
                else:
                    config.context.append(
                        {
                            "authority": "public",
                            "serial": len(config.context),
                            "round": config.current_round,
                            "speaker": "narrator",
                            "time": datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "content": "天亮了，昨晚是平安夜。",
                        }
                    )
                interact.printer(context=config.context)
                if game_over(is_game_over()):
                    return
            elif stage == "player_speech":
                public_speech()
                # generate_impressions()  # 发言后生成印象
            elif stage == "vote":
                # 投票阶段
                vote_target = public_vote(config.context)  # 调用公共投票逻辑
                interact.printer(context=config.context)
                if vote_target:
                    if config.players[vote_target - 1].role == "idiot":
                        config.context.append(
                            {
                                "authority": "public",
                                "serial": len(config.context),
                                "round": config.current_round,
                                "speaker": "narrator",
                                "time": datetime.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "content": f"由于{config.players[public_vote(config.context) - 1].id}号玩家是白痴，他不会被杀死。",
                            }
                        )
                        interact.printer(context=config.context)
                    elif config.players[vote_target - 1].role == "hunter":
                        hunter_action(vote_target)
                    if game_over(is_game_over()):
                        return

            else:
                print(f"未知阶段: {stage}")
