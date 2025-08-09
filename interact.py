import datetime
import os

import init


def printer(context, last_printed=[0]):
    """
    检查 context 是否有新增内容，有则打印新增内容。
    last_printed: 记录上次打印到的位置，默认用可变对象实现静态变量效果。
    """
    new_items = context[last_printed[0] :]
    for item in new_items:
        print(f"[{item['time']}] ({item['speaker']}) {item['content']}")
    last_printed[0] = len(context)


# ...existing code...


def generate_log(content):
    """
    生成日志文件。
    """
    log_dir = f"history/{init.sts}"
    os.makedirs(log_dir, exist_ok=True)  # 新增：确保目录存在
    with open(
        f"{log_dir}/back_end.log",
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {content}\n"
        )


def generate_action(content):
    """
    生成日志文件。
    """
    log_dir = f"history/{init.sts}"
    os.makedirs(log_dir, exist_ok=True)  # 新增：确保目录存在
    with open(
        f"{log_dir}/front_end.log",
        "a",
        encoding="utf-8",
    ) as f:
        f.write(
            f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {content}\n"
        )
