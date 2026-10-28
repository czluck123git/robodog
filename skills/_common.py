"""skill 共享工具

供 skills/ 目录下各 skill.py 复用的公共常量和函数。
"""
from typing import List

from robodog.config import UserMode
from robodog.factory_actions import EXCLUDED_ACTIONS, FactoryAction

# 移动方向 -> (vx符号, vy符号)，与 GUI 键盘映射保持一致
MOVE_VECTORS = {
    'forward': (1.0, 0.0),
    'backward': (-1.0, 0.0),
    'left': (0.0, 1.0),
    'right': (0.0, -1.0),
}

# 转向方向 -> wz符号（左转为正，与 GUI 保持一致）
TURN_SIGNS = {
    'left': 1.0,
    'right': -1.0,
}

# 用户模式名（小写）-> UserMode
USER_MODES = {mode.name.lower(): mode for mode in UserMode}


def stop_all(dog) -> None:
    """机器狗所有运动停止（线速度和角速度归零）"""
    dog.vx = 0.0
    dog.vy = 0.0
    dog.wz = 0.0


def get_available_actions(context) -> List[FactoryAction]:
    """获取可用原厂动作列表（按 context.filter_dangerous 过滤危险动作）"""
    actions = context.factory.get_available_actions(timeout=5.0)
    if context.filter_dangerous:
        actions = [a for a in actions if a.name not in EXCLUDED_ACTIONS]
    return actions


def resolve_action(actions: List[FactoryAction], action) -> FactoryAction:
    """按名称（不区分大小写，支持唯一前缀）或ID解析动作"""
    text = str(action).strip()
    # ID 匹配
    try:
        aid = int(text)
        for a in actions:
            if a.action_id == aid:
                return a
        raise ValueError(f"动作ID {aid} 不在可用列表中（可能已被过滤或不存在）")
    except ValueError:
        if text.isdigit():
            raise
    # 名称匹配
    for a in actions:
        if a.name.lower() == text.lower():
            return a
    matches = [a for a in actions if a.name.lower().startswith(text.lower())]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        names = ', '.join(m.name for m in matches)
        raise ValueError(f"动作名 '{text}' 有多个匹配: {names}，请写完整名称")
    raise ValueError(f"动作 '{text}' 不在可用列表中（可能已被过滤或不存在）")
