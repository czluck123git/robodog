"""set-body-height skill 实现: 设置机器狗机体高度"""
from robodog.skill import SkillResult


def get_handler(context):
    dog = context.dog

    def handle(height_m: float) -> SkillResult:
        dog.body_height = height_m
        return SkillResult(True, f"机体高度已设置为 {height_m}m")

    return handle
