"""turn skill 实现: 控制机器狗原地转向指定时长，结束后自动停止"""
import time

from robodog.skill import SkillResult

from skills._common import TURN_SIGNS


def get_handler(context):
    dog = context.dog

    def handle(direction: str, speed: float, duration: float) -> SkillResult:
        dog.wz = TURN_SIGNS[direction] * speed
        try:
            time.sleep(duration)
        finally:
            dog.wz = 0.0
        return SkillResult(True, f"向{direction}转向完成: 速度{speed}rad/s 持续{duration}s")

    return handle
