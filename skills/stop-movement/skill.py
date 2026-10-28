"""stop-movement skill 实现: 停止机器狗所有运动"""
from robodog.skill import SkillResult

from skills._common import stop_all


def get_handler(context):
    dog = context.dog

    def handle() -> SkillResult:
        stop_all(dog)
        return SkillResult(True, "已停止所有运动")

    return handle
