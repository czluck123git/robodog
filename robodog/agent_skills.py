"""机器狗 Agent Skill 接口

从 skills/ 目录加载技能文件（OpenClaw / Codex 组织规范：每个技能一个目录，
含 SKILL.md + schema.json + skill.py），封装基础运动能力和原厂动作，
供 Agent(如 LLM) 以统一方式调用。

用法:
    from robodog.agent_skills import AgentSkills

    skills = AgentSkills.connect('192.168.101.215')

    # 获取所有 skill 定义（用于注册到 LLM 工具列表）
    for schema in skills.list_skills():
        ...

    # 调用 skill（同步执行，返回可 JSON 序列化的 dict）
    result = skills.call('move', direction='forward', speed=0.5, duration=2)
    result = skills.call('run-factory-action', action='Shake hand')
"""
from typing import List, Optional

from .dog import Dog
from .factory_actions import FactoryActions
from .skill import Skill, SkillResult
from .skill_loader import SkillContext, SkillLoader

__all__ = ['AgentSkills', 'Skill', 'SkillResult']


class AgentSkills:
    """机器狗 skill 注册与调用中心

    参数:
        dog: 已连接的 Dog 实例
        factory_actions: FactoryActions 实例，提供后可使用原厂动作 skill
        filter_dangerous: 是否过滤空翻/站立/撒娇/跳跃等动作（默认开启）
        skills_dir: 技能目录，默认 <仓库根>/skills
        autoload: 是否自动从技能目录加载（默认开启）
    """

    def __init__(self, dog: Dog,
                 factory_actions: Optional[FactoryActions] = None,
                 filter_dangerous: bool = True,
                 skills_dir: Optional[str] = None,
                 autoload: bool = True):
        self.dog = dog
        self.factory = factory_actions
        self.filter_dangerous = filter_dangerous
        self._skills = {}
        if autoload:
            self._load_from_disk(skills_dir)

    # ------------------------------------------------------------------
    # 连接便捷方法
    # ------------------------------------------------------------------
    @classmethod
    def connect(cls, host: str = '192.168.101.215', port: int = 9090,
                filter_dangerous: bool = True) -> 'AgentSkills':
        """连接机器狗并创建 skill 中心"""
        dog = Dog(host=host, port=port).connect()
        return cls(dog, FactoryActions(dog._client.client),
                   filter_dangerous=filter_dangerous)

    # ------------------------------------------------------------------
    # 磁盘加载
    # ------------------------------------------------------------------
    def _load_from_disk(self, skills_dir: Optional[str] = None) -> None:
        loader = SkillLoader(skills_dir)
        context = SkillContext(dog=self.dog, factory=self.factory,
                               filter_dangerous=self.filter_dangerous)
        self.loaded_skills: List[str] = loader.load_into(self, context)

    # ------------------------------------------------------------------
    # 注册 / 查询 / 调用
    # ------------------------------------------------------------------
    def register(self, skill: Skill) -> None:
        """注册自定义 skill"""
        self._skills[skill.name] = skill

    def list_skills(self) -> List[dict]:
        """返回所有 skill 的 schema 列表，用于注册到 LLM 工具"""
        return [skill.schema() for skill in self._skills.values()]

    def call(self, name: str, **params) -> dict:
        """调用指定 skill，返回可 JSON 序列化的结果 dict"""
        skill = self._skills.get(name)
        if not skill:
            available = ', '.join(sorted(self._skills.keys()))
            return SkillResult(False, f"未知的skill: '{name}'，可用: {available}").to_dict()
        try:
            clean = self._validate(skill, params)
            return skill.handler(**clean).to_dict()
        except Exception as e:
            return SkillResult(False, f"skill '{name}' 调用失败: {e}").to_dict()

    # ------------------------------------------------------------------
    # 参数校验（JSON Schema 子集：required/enum/type/minimum/maximum）
    # ------------------------------------------------------------------
    def _validate(self, skill: Skill, params: dict) -> dict:
        schema = skill.parameters or {}
        props = schema.get('properties', {})
        required = schema.get('required', [])

        for key in required:
            if key not in params or params[key] is None:
                raise ValueError(f"缺少必填参数: {key}")

        unknown = set(params) - set(props)
        if unknown:
            raise ValueError(f"未知参数: {', '.join(sorted(unknown))}")

        clean = dict(params)
        for key, value in clean.items():
            spec = props[key]
            if 'enum' in spec:
                if value not in spec['enum']:
                    # 字符串枚举不区分大小写，并归一化为标准值
                    lowered = {str(e).lower(): e for e in spec['enum']}
                    if isinstance(value, str) and value.lower() in lowered:
                        value = clean[key] = lowered[value.lower()]
                    else:
                        raise ValueError(
                            f"参数 {key} 必须是 {spec['enum']} 之一，收到: {value!r}")
            ptype = spec.get('type')
            if ptype == 'number':
                value = float(value)
                self._check_range(key, value, spec)
                clean[key] = value
            elif ptype == 'integer':
                value = int(value)
                self._check_range(key, value, spec)
                clean[key] = value
            elif ptype == 'string' and not isinstance(value, str):
                clean[key] = str(value)
        return clean

    @staticmethod
    def _check_range(key: str, value, spec: dict) -> None:
        if 'minimum' in spec and value < spec['minimum']:
            raise ValueError(f"参数 {key} 不能小于 {spec['minimum']}，收到: {value}")
        if 'maximum' in spec and value > spec['maximum']:
            raise ValueError(f"参数 {key} 不能大于 {spec['maximum']}，收到: {value}")
