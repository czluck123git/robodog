"""move skill 实现: 控制机器狗朝指定方向移动指定时长，结束后自动停止"""
import time

from robodog.skill import SkillResult

from skills._common import MOVE_VECTORS


def get_handler(context):
    dog = context.dog

    def handle(direction: str, speed: float, duration: float) -> SkillResult:
        sign_x, sign_y = MOVE_VECTORS[direction]
        dog.vx = sign_x * speed
        dog.vy = sign_y * speed
        try:
            time.sleep(duration)
        finally:
            dog.vx = 0.0
            dog.vy = 0.0
        return SkillResult(True, f"向{direction}移动完成: 速度{speed}m/s 持续{duration}s")

    return handle
