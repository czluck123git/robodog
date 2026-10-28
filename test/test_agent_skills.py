"""
机器狗 Agent Skill 接口测试

离线测试使用桩对象验证注册/校验/调用逻辑（无需机器人），
加 --robot 参数可连接真实机器人做端到端验证。
"""

import sys

sys.path.append('.')
sys.path.append('..')

from robodog.agent_skills import AgentSkills, Skill, SkillResult
from robodog.factory_actions import FactoryAction, EXCLUDED_ACTIONS
from robodog.config import UserMode


class StubState:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class StubDog:
    """模拟 Dog 的最小接口"""

    def __init__(self):
        self.vx = self.vy = self.wz = 0.0
        self.body_height = 0.23
        self.roll = self.pitch = self.yaw = 0.0
        self.user_mode = None
        self.ctrl_state = StubState(user_mode=3, standing=True, estop=False, error=False)
        self.body_status = StubState(x=1.0, y=2.0, z=0.25, roll=0.1, pitch=0.2,
                                     yaw=0.3, vx=0.0, vy=0.0, wz=0.0)

    def set_user_mode(self, mode):
        self.user_mode = mode

    def is_state_valid(self):
        return True


ALL_ACTIONS = [
    FactoryAction(1, 'Wake'), FactoryAction(5, 'Sit down'), FactoryAction(2, 'Get down'),
    FactoryAction(3, 'Recovery stand'), FactoryAction(273, 'Sway'),
    FactoryAction(514, 'Shake hand'), FactoryAction(625, 'Dynamic dance'),
    FactoryAction(260, 'Back flip'), FactoryAction(545, 'Coax'), FactoryAction(257, 'Jump'),
]


class StubFactory:
    """模拟 FactoryActions 的最小接口"""

    def __init__(self):
        self.ran = []
        self.cancelled = False

    def get_available_actions(self, timeout=5.0):
        return list(ALL_ACTIONS)

    def run_action(self, action_id, timeout=None, feedback_cb=None):
        self.ran.append(action_id)
        return 0, 'SUCCEEDED'

    def cancel(self):
        self.cancelled = True
        return True


def check(cond, msg):
    if cond:
        print(f"   ✅ {msg}")
    else:
        print(f"   ❌ {msg}")
        raise AssertionError(msg)


def test_registration():
    """测试 skill 注册与 schema 导出"""
    print("1. 测试 skill 注册与 schema...")
    skills = AgentSkills(StubDog(), StubFactory())
    schemas = skills.list_skills()
    check(len(schemas) == 11, f"共注册 {len(schemas)} 个skill (8运动+3动作)")
    names = {s['name'] for s in schemas}
    expected = {'move', 'turn', 'set-velocity', 'stop-movement', 'set-body-height',
                'set-user-mode', 'reset-posture', 'get-robot-status',
                'list-factory-actions', 'run-factory-action', 'cancel-factory-action'}
    check(names == expected, f"skill名称齐全: {sorted(names)}")
    for s in schemas:
        check('name' in s and 'description' in s and 'parameters' in s,
              f"schema '{s['name']}' 结构完整")
    return skills


def test_movement(skills):
    """测试基础运动 skill"""
    print("\n2. 测试基础运动 skill...")
    dog = skills.dog

    r = skills.call('move', direction='forward', speed=0.5, duration=0.1)
    check(r['success'] and dog.vx == 0.0 and dog.vy == 0.0, "move后自动停止")
    check(dog.vx == 0.0, "vx已归零")

    # 方向映射正确性（通过set_velocity间接验证符号约定）
    skills.call('set-velocity', vx=1.0, vy=-1.0, wz=0.5)
    check(dog.vx == 1.0 and dog.vy == -1.0 and dog.wz == 0.5, "set_velocity设置正确")
    skills.call('stop-movement')
    check(dog.vx == 0.0 and dog.vy == 0.0 and dog.wz == 0.0, "stop_movement归零")

    r = skills.call('turn', direction='left', speed=1.0, duration=0.1)
    check(r['success'] and dog.wz == 0.0, "turn后自动停止")

    r = skills.call('set-body-height', height_m=0.3)
    check(r['success'] and dog.body_height == 0.3, "set_body_height生效")

    r = skills.call('set-user-mode', mode='DANCE')
    check(r['success'] and dog.user_mode == UserMode.DANCE, "set_user_mode不区分大小写")

    skills.call('set-velocity', vx=1.0, vy=1.0, wz=1.0)
    r = skills.call('reset-posture')
    check(r['success'] and dog.vx == 0.0 and dog.body_height == 0.23 and dog.pitch == 0.0,
          "reset_posture恢复默认")

    r = skills.call('get-robot-status')
    check(r['success'] and r['data']['user_mode'] == 'NORMAL', "get_robot_status返回状态")


def test_validation(skills):
    """测试参数校验"""
    print("\n3. 测试参数校验...")
    r = skills.call('move', direction='up', speed=0.5, duration=1)
    check(not r['success'] and '必须是' in r['message'], "非法direction被拒绝")

    r = skills.call('move', direction='forward', speed=99, duration=1)
    check(not r['success'] and '不能大于' in r['message'], "超速被拒绝")

    r = skills.call('move', direction='forward', speed=0.5)
    check(not r['success'] and '缺少必填参数' in r['message'], "缺少duration被拒绝")

    r = skills.call('move', direction='forward', speed=0.5, duration=1, extra=1)
    check(not r['success'] and '未知参数' in r['message'], "未知参数被拒绝")

    r = skills.call('not_exist')
    check(not r['success'] and '未知的skill' in r['message'], "未知skill被拒绝")


def test_factory_actions(skills):
    """测试原厂动作 skill"""
    print("\n4. 测试原厂动作 skill...")
    factory = skills.factory

    r = skills.call('list-factory-actions')
    check(r['success'], "list_factory_actions成功")
    names = [a['name'] for a in r['data']]
    check(len(names) == len(ALL_ACTIONS) - len(EXCLUDED_ACTIONS & {a.name for a in ALL_ACTIONS}),
          f"危险动作已过滤，剩余 {len(names)} 个")
    check('Back flip' not in names and 'Coax' not in names and 'Jump' not in names,
          "空翻/撒娇/跳跃不在列表中")
    check('Shake hand' in names, "握手保留")

    r = skills.call('run-factory-action', action='Shake hand')
    check(r['success'] and factory.ran == [514], "按名称执行动作(ID=514)")

    r = skills.call('run-factory-action', action='sit')
    check(r['success'] and factory.ran[-1] == 5, "前缀模糊匹配 Sit down")

    r = skills.call('run-factory-action', action='273')
    check(r['success'] and factory.ran[-1] == 273, "按ID执行动作")

    r = skills.call('run-factory-action', action='Back flip')
    check(not r['success'], "已过滤动作被拒绝")

    r = skills.call('cancel-factory-action')
    check(r['success'] and factory.cancelled, "cancel_factory_action生效")


def test_custom_skill(skills):
    """测试自定义 skill 注册"""
    print("\n5. 测试自定义 skill 注册...")

    def handler(times=1):
        return SkillResult(True, f"叫{times}声", data={'sound': '汪' * int(times)})

    skills.register(Skill(
        name='bark',
        description='让机器狗叫',
        parameters={
            'type': 'object',
            'properties': {'times': {'type': 'integer', 'minimum': 1, 'maximum': 5}},
            'required': ['times'],
        },
        handler=handler,
    ))
    r = skills.call('bark', times=3)
    check(r['success'] and r['data']['sound'] == '汪汪汪', "自定义skill调用成功")


def test_robot(host='192.168.101.215'):
    """真实机器人端到端测试（可选）"""
    print("\n" + "=" * 60)
    print(f"🤖 真机端到端测试: {host}")
    print("=" * 60)

    skills = AgentSkills.connect(host)
    print(f"   ✅ 已连接 {host}")
    import time
    time.sleep(3)  # 等待状态订阅回流（机器人刚启动时需更久）

    r = skills.call('get-robot-status')
    check(r['success'], f"状态: standing={r['data']['standing']} z={r['data']['position']['z']:.2f} mode={r['data']['user_mode']} state_valid={r['data']['state_valid']}")
    if not r['data']['state_valid']:
        print("   ⚠️ 状态数据尚未回流(state_valid=false)，机器人可能刚启动，等待5秒重试...")
        time.sleep(5)
        r = skills.call('get-robot-status')
        print(f"   重试: standing={r['data']['standing']} z={r['data']['position']['z']:.2f} state_valid={r['data']['state_valid']}")

    r = skills.call('list-factory-actions')
    check(r['success'], f"可用动作 {len(r['data'])} 个: {[a['name'] for a in r['data']][:8]}...")

    r = skills.call('run-factory-action', action='Recovery stand')
    check(r['success'], f"恢复站立: {r['message']}")
    time.sleep(2)

    r = skills.call('run-factory-action', action='Shake hand')
    check(r['success'], f"执行握手: {r['message']}")
    time.sleep(2)

    r = skills.call('run-factory-action', action='Recovery stand')
    check(r['success'], f"恢复站立: {r['message']}")

    skills.dog.disconnect()
    print("\n🎉 真机端到端测试通过!")


if __name__ == '__main__':
    try:
        skills = test_registration()
        test_movement(skills)
        test_validation(skills)
        test_factory_actions(skills)
        test_custom_skill(skills)
        print("\n🎉 全部离线测试通过!")
        if '--robot' in sys.argv:
            test_robot()
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
