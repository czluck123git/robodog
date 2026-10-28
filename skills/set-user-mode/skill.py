"""set-user-mode skill 实现: 设置机器狗用户模式"""
from robodog.skill import SkillResult

from skills._common import USER_MODES


def get_handler(context):
    dog = context.dog

    def handle(mode: str) -> SkillResult:
        user_mode = USER_MODES.get(str(mode).lower())
        if user_mode is None:
            raise ValueError(f"未知的用户模式: {mode}，可用: {sorted(USER_MODES.keys())}")
        dog.set_user_mode(user_mode)
        return SkillResult(True, f"用户模式已设置为 {user_mode.name}")

    return handle
