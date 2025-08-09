import call
import config


# 新增辅助函数：从上下文中提取关键信息
def extract_key_context(context):
    """
    调用大模型提取上下文中的关键信息，返回一个精简的摘要。
    """
    import json

    # 筛选最近10条消息作为示例（也可以根据实际需要调整）
    send_context = json.dumps(context, ensure_ascii=False)

    # 构造消息，注意此处的系统提示要求返回仅包含关键信息的摘要
    messages = [
        {
            "role": "system",
            "content": """
你是一个狼人杀游戏的文本摘要助手。请根据下面给出的游戏聊天记录，提取并总结本局游戏中的关键事件和重要决策，特别关注：

- 狼人阵营的讨论和决策过程，包括他们的目标和达成的共识；
- 女巫的行动选择及其结果；
- 预言家的查验结果及公开身份；
- 白天发言阶段的主要争议和关键发言。

请将总结写成一段连贯的自然语言描述，突出事件的因果关系和玩家之间的互动，不要简单罗列聊天内容。总结应简洁明了，避免无关细节。

请用中文输出，将摘要文本包含在json中的"content"字段当中。

下面是聊天记录：
""",
        },
        {"role": "user", "content": send_context},
    ]

    # 调用安全包装的 API 调用函数
    summary = call.safe_caller(messages)
    return summary


# 函数：筛选上下文中对玩家可见的信息
def context_filter(player_id):
    """
    根据玩家ID筛选上下文信息，返回该玩家可见的内容。
    """
    send_context = [
        item
        for item in config.context
        if item.get("authority") == "public"
        or (
            isinstance(item.get("authority"), list)
            and player_id in item.get("authority")
        )
        or item.get("authority") == player_id
    ]
    return send_context


# 用于发言
def generate_roles_msg(p, send_context):
    import json

    match p.role:
        case "werewolf":
            messages = [
                {
                    "role": "system",
                    "content": call.werewolf_system_prompt.format(p.id),
                },
                {
                    "role": "user",
                    "content": json.dumps(send_context, ensure_ascii=False),
                },
            ]
        case "witch":
            messages = [
                {
                    "role": "system",
                    "content": call.witch_system_prompt.format(p.id),
                },
                {
                    "role": "user",
                    "content": json.dumps(send_context, ensure_ascii=False),
                },
            ]
        case "seer":
            messages = [
                {
                    "role": "system",
                    "content": call.seer_system_prompt.format(p.id),
                },
                {
                    "role": "user",
                    "content": json.dumps(send_context, ensure_ascii=False),
                },
            ]
        case "hunter":
            messages = [
                {
                    "role": "system",
                    "content": call.hunter_system_prompt.format(p.id),
                },
                {
                    "role": "user",
                    "content": json.dumps(send_context, ensure_ascii=False),
                },
            ]
        case "idiot":
            messages = [
                {
                    "role": "system",
                    "content": call.idiot_system_prompt.format(p.id),
                },
                {
                    "role": "user",
                    "content": json.dumps(send_context, ensure_ascii=False),
                },
            ]
        case "villager":
            messages = [
                {
                    "role": "system",
                    "content": call.villager_system_prompt.format(p.id),
                },
                {
                    "role": "user",
                    "content": json.dumps(send_context, ensure_ascii=False),
                },
            ]
    return messages


def assemble_llm_context(visible_context, recent, instruction):
    """
    构造发送给 LLM 的上下文，其由三部分组成：
    1. 对当前玩家可见的上下文的精简版（由 lib.context_filter 获得）
    2. 对模型的指令：来自当前流程的指令文本
    """
    summary_context = extract_key_context(visible_context)  # (1) 精简版上下文
    # (3) 将 instruction 封装为一个系统级消息结构（此处 role 设为 "system"）
    final_context = {
        "summary_speech_history": summary_context,
        "recent_messages": recent,
        "instruction": instruction,
    }
    # print(final_context)  # 调试选项
    return final_context
