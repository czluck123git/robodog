"""reset-posture skill 实现: 重置机器狗姿态"""
from robodog.skill import SkillResult

from skills._common import stop_all


def get_handler(context):
    dog = context.dog

    def handle() -> SkillResult:
        stop_all(dog)
        dog.body_height = 0.23
        dog.roll = 0.0
        dog.pitch = 0.0
        dog.yaw = 0.0
        return SkillResult(True, "姿态已重置")

    return handle
