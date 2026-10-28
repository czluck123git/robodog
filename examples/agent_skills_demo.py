"""
Agent Skill 调用示例

演示如何将机器狗的能力以 skill 方式提供给 Agent(如 LLM) 调用：
1. 注册所有 skill 的 schema 到工具列表
2. Agent 通过 call() 执行 skill
3. 展示基础运动和原厂动作的典型调用流程

运行: python examples/agent_skills_demo.py [--host 192.168.101.215]
"""
import json
import sys

from robodog.agent_skills import AgentSkills


def main():
    host = '192.168.101.215'
    if '--host' in sys.argv:
        host = sys.argv[sys.argv.index('--host') + 1]

    print(f"正在连接机器狗 {host} ...")
    skills = AgentSkills.connect(host)
    print("已连接")
    import time
    time.sleep(2)  # 等待状态订阅回流、机器人准备就绪

    # ---- 1. 导出所有 skill 的 schema（注册到 LLM 工具列表）----
    schemas = skills.list_skills()
    print(f"共 {len(schemas)} 个 skill，schema 示例:")
    print(json.dumps(schemas[0], ensure_ascii=False, indent=2))
    print("...")

    # ---- 2. 查询状态 ----
    result = skills.call('get-robot-status')
    print("\n[get_robot_status]")
    print(json.dumps(result, ensure_ascii=False))

    # ---- 3. 列出厂动作 ----
    result = skills.call('list-factory-actions')
    print("\n[list_factory_actions]")
    print(" ", result['message'])
    print(" ", [a['name'] for a in result['data']])

    # ---- 4. 基础运动: 前进1秒 ----
    print("\n[move] 前进 0.3m/s 持续1秒")
    result = skills.call('move', direction='forward', speed=0.3, duration=1)
    print(" ", result['message'])

    # ---- 5. 原厂动作: 先恢复站立，再握手 ----
    print("\n[run_factory_action] 恢复站立")
    result = skills.call('run-factory-action', action='Recovery stand')
    print(" ", result['message'])
    time.sleep(2)

    print("\n[run_factory_action] 握手")
    result = skills.call('run-factory-action', action='Shake hand')
    print(" ", result['message'])

    # ---- 6. 结束后恢复站立 ----
    time.sleep(2)
    print("\n[run_factory_action] 恢复站立")
    result = skills.call('run-factory-action', action='Recovery stand')
    print(" ", result['message'])

    # ---- 7. 演示错误处理: 非法参数 ----
    print("\n[非法参数示例]")
    result = skills.call('move', direction='up', speed=1, duration=1)
    print(" ", result['message'])

    skills.dog.disconnect()
    print("\n演示完成")


if __name__ == '__main__':
    main()
