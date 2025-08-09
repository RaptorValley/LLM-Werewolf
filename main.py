import json
import sys

import action
import config
import init
import interact
import call


if __name__ == "__main__":
    config.provider = sys.argv[1] if len(sys.argv) > 1 else "OpenAI"
    config.model_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    interact.generate_log(f"模型提供商：{config.provider}")
    interact.generate_log(f"模型名称：{call.selected_model}")
    action.game_loop()
    # 保存聊天上下文到json文件
    with open(f"history/{init.sts}/chat_history.json", "w", encoding="utf-8") as f:
        json.dump(config.context, f, ensure_ascii=False, indent=2)
