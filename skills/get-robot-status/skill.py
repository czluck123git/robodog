"""get-robot-status skill 实现: 获取机器狗当前状态"""
from robodog.config import UserMode
from robodog.skill import SkillResult


def get_handler(context):
    dog = context.dog

    def handle() -> SkillResult:
        ctrl = dog.ctrl_state
        body = dog.body_status
        try:
            mode_name = UserMode(ctrl.user_mode).name
        except ValueError:
            mode_name = str(ctrl.user_mode)
        data = {
            'user_mode': mode_name,
            'standing': ctrl.standing,
            'estop': ctrl.estop,
            'error': ctrl.error,
            'position': {'x': body.x, 'y': body.y, 'z': body.z},
            'rpy': {'roll': body.roll, 'pitch': body.pitch, 'yaw': body.yaw},
            'velocity': {'vx': body.vx, 'vy': body.vy, 'wz': body.wz},
            'state_valid': dog.is_state_valid(),
        }
        return SkillResult(True, "状态获取成功", data=data)

    return handle
