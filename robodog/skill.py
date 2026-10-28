"""Skill 基础数据结构

定义 Skill / SkillResult，作为 skills/ 目录下各技能文件的统一接口类型。
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass
class SkillResult:
    """skill 调用结果"""
    success: bool
    message: str
    data: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {'success': self.success, 'message': self.message, 'data': self.data}


@dataclass
class Skill:
    """Agent 可调用的 skill 定义

    参数:
        name: skill 名称（kebab-case，与文件夹名一致）
        description: 功能描述，用于注册到 LLM 工具列表
        parameters: JSON Schema (type=object)，描述参数和约束
        handler: 执行函数，签名为参数schema中各字段
        source: skill 文件所在目录名，便于追溯
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., SkillResult]
    source: str = ''

    def schema(self) -> Dict[str, Any]:
        """返回用于 LLM 工具注册的定义"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
        }
