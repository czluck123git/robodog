"""Skill 加载器

按照 OpenClaw / Codex 等 Agent 的 skill 组织规范，从 skills/ 目录发现并加载技能：

    skills/
    ├── <skill-name>/
    │   ├── SKILL.md      # YAML frontmatter: name, description + 使用说明
    │   ├── schema.json   # 参数 JSON Schema（可选，用于LLM工具注册）
    │   └── skill.py      # 实现文件，需提供 get_handler(context)
    └── ...

skill.py 约定:
    def get_handler(context):   # context 为 SkillContext
        def handle(**params): ...   # 返回 SkillResult
        return handle
"""
import importlib.util
import json
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from .skill import Skill

# 默认 skills 目录：<仓库根>/skills
DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent / 'skills'


@dataclass
class SkillContext:
    """传递给 skill 处理器的运行上下文"""
    dog: Any                      # 已连接的 robodog.Dog 实例
    factory: Any = None           # robodog.factory_actions.FactoryActions 实例
    filter_dangerous: bool = True # 是否过滤危险的原厂动作


@dataclass
class SkillDef:
    """从磁盘发现的一个 skill 定义（元数据部分）"""
    name: str
    description: str
    parameters: dict
    directory: Path


def parse_frontmatter(text: str) -> dict:
    """解析 Markdown 文件头部的 YAML frontmatter（仅支持 key: value 单行）"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}
    meta = {}
    for line in lines[1:]:
        if line.strip() == '---':
            break
        key, sep, value = line.partition(':')
        if sep:
            meta[key.strip()] = value.strip().strip('"\'')
    return meta


class SkillLoader:
    """发现并加载 skills/ 目录下的技能文件"""

    def __init__(self, skills_dir: Optional[str | Path] = None):
        self.skills_dir = Path(skills_dir) if skills_dir else DEFAULT_SKILLS_DIR

    def discover(self) -> List[SkillDef]:
        """扫描 skills 目录，返回所有含 SKILL.md 的 skill 定义"""
        if not self.skills_dir.is_dir():
            warnings.warn(f'未找到 skills 目录: {self.skills_dir}')
            return []

        defs = []
        for sub in sorted(self.skills_dir.iterdir()):
            if not sub.is_dir() or sub.name.startswith(('_', '.')):
                continue
            skill_md = sub / 'SKILL.md'
            if not skill_md.exists():
                continue
            meta = parse_frontmatter(skill_md.read_text(encoding='utf-8'))
            schema_file = sub / 'schema.json'
            if schema_file.exists():
                parameters = json.loads(schema_file.read_text(encoding='utf-8'))
            else:
                parameters = {'type': 'object', 'properties': {}}
            defs.append(SkillDef(
                name=meta.get('name') or sub.name,
                description=meta.get('description', ''),
                parameters=parameters,
                directory=sub,
            ))
        return defs

    def load_into(self, registry, context: SkillContext) -> List[str]:
        """加载所有含 skill.py 的技能到 registry（需提供 register 方法），返回已加载名称"""
        # 保证 skills 包可导入（skill.py 中可使用 from skills._common import ...）
        repo_root = str(self.skills_dir.parent)
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)

        loaded = []
        for sd in self.discover():
            module_path = sd.directory / 'skill.py'
            if not module_path.exists():
                continue  # 纯文档 skill，跳过
            module_name = f"robodog_skill_{sd.directory.name.replace('-', '_')}"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                handler = module.get_handler(context)
            except Exception as e:
                warnings.warn(f"加载 skill '{sd.name}' 失败: {e}")
                continue
            registry.register(Skill(
                name=sd.name,
                description=sd.description,
                parameters=sd.parameters,
                handler=handler,
                source=sd.directory.name,
            ))
            loaded.append(sd.name)
        return loaded
