"""list-factory-actions skill 实现: 获取可用原厂动作列表"""
from robodog.skill import SkillResult

from skills._common import get_available_actions


def get_handler(context):
    def handle() -> SkillResult:
        actions = get_available_actions(context)
        data = [{'id': a.action_id, 'name': a.name} for a in actions]
        return SkillResult(True, f"共 {len(actions)} 个可用原厂动作", data=data)

    return handle
