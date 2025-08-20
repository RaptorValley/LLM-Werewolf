import openai
import json
import re
import datetime

import lib
import config
import init
import interact

basic_info = [
    {
        "provider": "OpenAI",
        "api_key": "<YOUR-API-HERE>",
        "base_url": "https://api.openai.com/v1/",
        "model_list": [
            "gpt-4.1",
            "gpt-4.1-mini",
        ],
    },
    {
        "provider": "ZhipuAI",
        "api_key": "<YOUR-API-HERE>",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model_list": [
            "glm-4.5",
            "glm-4.5-x",
        ],
    },
    {
        "provider": "DeepSeek",
        "api_key": "<YOUR-API-HERE>",
        "base_url": "https://api.deepseek.com/",
        "model_list": [
            "deepseek-chat",
            "deepseek-reasoner",
        ],
    },
    {
        "provider": "SiliconFlow",
        "api_key": "<YOUR-API-HERE>",
        "base_url": "https://api.siliconflow.cn/v1/",
        "model_list": [
            "Qwen/Qwen3-235B-A22B",
            "deepseek-ai/DeepSeek-R1",
            "zai-org/GLM-4.5",
            "Pro/moonshotai/Kimi-K2-Instruct",
        ],
    },
]

"""
for info in basic_info:
    if info["provider"] == config.provider:
        openai.api_key = info["api_key"]
        openai.base_url = info["base_url"]
        selected_model = info["model_list"][config.model_index]
        break
"""

openai.api_key = "<YOUR-API-HERE>"
openai.base_url = "https://open.bigmodel.cn/api/paas/v4/"
selected_model = "glm-4.5"


def save_response_to_file(response: str):
    with open(f"history/{init.sts}/original_output.txt", "a", encoding="utf-8") as f:
        f.write(
            f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] "{selected_model}"\n{response}\n\n'
        )


def call_openai_api(conoriginal_response):
    response = openai.chat.completions.create(
        model=selected_model,
        messages=conoriginal_response,
        response_format={
            "type": "json_object",
        },
    )

    return response.choices[0].message.content


def safe_caller(message: str, type="content"):
    while True:
        try:
            original_response = call_openai_api(message)
            original_response = original_response.strip()
            if original_response.startswith("```json"):
                original_response = original_response[len("```json") :].strip()
            elif original_response.startswith("```"):
                original_response = original_response[len("```") :].strip()
            if original_response.endswith("```"):
                original_response = original_response[: -len("```")].strip()
            # 只截取第一个大括号之间的内容
            match = re.search(r"\{[^{}]*\}", original_response)
            if match:
                original_response = match.group(0)
            interact.generate_log("成功截取模型响应")
            save_response_to_file(original_response)
            interact.generate_log("成功保存模型响应")
            result = json.loads(original_response)[type]
            interact.generate_log("成功解析模型响应")
            return result
        except Exception:
            continue


def complete_caller(pid: int, ins: str, type="content"):
    """
    完整构建上下文，并获取响应。
    参数：
        pid 玩家id
        ins 指令
        type 用于safe_caller，默认为"content"
    返回值(str)：
        模型的回复
    """
    visible_context = lib.context_filter(pid)  # 筛选可见信息
    interact.generate_log("成功筛选可见信息")
    content = lib.assemble_llm_context(
        pid, visible_context, config.players[pid - 1].recent_msg, ins["content"]
    )
    interact.generate_log("成功组织上下文")
    messages = lib.generate_roles_msg(config.players[pid - 1], content)  # 构建prompt
    interact.generate_log("成功构建提示词")
    response = safe_caller(messages, type=type)  # 生成响应
    return response


prompt_dict = {
    "head": lib.file_process("prompt/head.txt"),
    "speech": lib.file_process("prompt/speech.txt"),
    "action": lib.file_process("prompt/action.txt"),
    "tips": lib.file_process("prompt/tips.json"),
}

"""
当全体玩家发言结束后，系统会引导您更新对每名玩家的印象。每次输出时只需发送对**一名**玩家的印象，格式为：
{{
    "content": ......,
    "role": ......
}}
"content"是您对它的具体印象，需要用简短的语言来描述；"role"则是您对其可能身份的猜测。
"""
