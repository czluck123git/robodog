"""cancel-factory-action skill 实现: 取消当前正在执行的原厂动作"""
from robodog.skill import SkillResult


def get_handler(context):
    factory = context.factory

    def handle() -> SkillResult:
        if factory.cancel():
            return SkillResult(True, "已发送取消请求")
        return SkillResult(False, "当前没有正在执行的原厂动作")

    return handle
