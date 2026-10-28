"""run-factory-action skill 实现: 执行机器人原厂内置动作并等待结束"""
from robodog.skill import SkillResult

from skills._common import get_available_actions, resolve_action, stop_all


def get_handler(context):
    dog = context.dog
    factory = context.factory

    def handle(action: str, timeout: float = 60.0) -> SkillResult:
        actions = get_available_actions(context)
        resolved = resolve_action(actions, action)

        # 执行动作前先停止运动，避免速度指令干扰
        stop_all(dog)

        code, status = factory.run_action(resolved.action_id, timeout=timeout)
        if code == 0:
            return SkillResult(True, f"原厂动作 '{resolved.name}' 执行完成 ({status})")
        return SkillResult(
            False,
            f"原厂动作 '{resolved.name}' 执行异常: result={code} ({status})，"
            "动作可能被机器人拒绝（如机器狗趴下或空间不足），可先执行 'Recovery stand' 后重试")

    return handle
