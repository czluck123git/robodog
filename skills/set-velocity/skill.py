"""set-velocity skill 实现: 直接设置线速度和角速度(高级用法，需配合 stop-movement)"""
from robodog.skill import SkillResult


def get_handler(context):
    dog = context.dog

    def handle(vx: float, vy: float, wz: float) -> SkillResult:
        dog.vx = vx
        dog.vy = vy
        dog.wz = wz
        return SkillResult(True, f"速度已设置: vx={vx} vy={vy} wz={wz}")

    return handle
