"""命令行调用 skill

用法:
    # 列出所有 skill 及其 schema
    python -m robodog.skill_cli list

    # 调用 skill（key=value 传参）
    python -m robodog.skill_cli move direction=forward speed=0.5 duration=2
    python -m robodog.skill_cli run-factory-action action="Shake hand"

    # 指定机器人地址
    python -m robodog.skill_cli --host 192.168.101.215 move direction=forward speed=0.5 duration=2
"""
import json
import sys

from .agent_skills import AgentSkills


def _coerce(value: str):
    """将字符串参数转为 int/float/str"""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        return 0

    host = '192.168.101.215'
    if '--host' in args:
        i = args.index('--host')
        host = args[i + 1]
        del args[i:i + 2]

    if not args:
        print(__doc__)
        return 0

    if args[0] == 'list':
        # 只列出 schema，不连接机器人（handler 持有 dog=None，但 list 不会触发执行）
        skills = AgentSkills(None, autoload=False)
        skills._load_from_disk()
        print(json.dumps(skills.list_skills(), ensure_ascii=False, indent=2))
        return 0

    name, *kv_args = args
    params = {}
    for arg in kv_args:
        key, sep, value = arg.partition('=')
        if not sep:
            print(f"参数格式错误: {arg!r}，应为 key=value", file=sys.stderr)
            return 2
        params[key] = _coerce(value)

    skills = AgentSkills.connect(host)
    result = skills.call(name, **params)
    print(json.dumps(result, ensure_ascii=False))
    skills.dog.disconnect()
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
