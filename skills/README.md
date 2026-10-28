# 机器狗技能集 (RoboDog Skills)

按照 OpenClaw / Codex 等 Agent 的 skill 规范组织的机器狗技能集，
涵盖**基础运动能力**和**原厂动作**两大类，供 Agent(如 LLM) 调用。

## 目录结构

每个技能一个独立目录，包含三个文件：

```
skills/
├── <skill-name>/            # 技能目录名 = skill 名称（kebab-case）
│   ├── SKILL.md             # 技能说明：YAML frontmatter(name/description) + 参数/示例/注意事项
│   ├── schema.json          # 参数 JSON Schema（用于 LLM 工具注册）
│   └── skill.py             # 实现文件，需提供 get_handler(context)
├── _common.py               # 各技能共享的工具函数（不视为技能）
└── README.md
```

`skill.py` 约定：

```python
def get_handler(context):
    """context: SkillContext(dog, factory, filter_dangerous)"""
    def handle(**params):   # 参数与 schema.json 对应
        ...                 # 返回 SkillResult
    return handle
```

## 技能清单

### 基础运动

| 技能 | 说明 |
|---|---|
| `move` | 朝指定方向移动指定时长，自动停止 |
| `turn` | 原地左/右转指定时长，自动停止 |
| `set-velocity` | 直接设置 vx/vy/wz（高级，需配合 stop-movement） |
| `stop-movement` | 停止所有运动 |
| `set-body-height` | 设置机体高度 0.09~0.35m |
| `set-user-mode` | 设置用户模式（normal/kids/dance/quiet/mute/extreme/long_endurance） |
| `reset-posture` | 重置姿态（速度归零、默认身高、水平姿态） |
| `get-robot-status` | 获取状态（模式/位姿/速度/站立状态） |

### 原厂动作

| 技能 | 说明 |
|---|---|
| `list-factory-actions` | 获取可用原厂动作列表 |
| `run-factory-action` | 执行原厂动作（支持名称/唯一前缀/ID） |
| `cancel-factory-action` | 取消正在执行的原厂动作 |

## 使用方式

### 1. 命令行直接调用

```bash
# 列出所有技能 schema（不连接机器人）
python -m robodog.skill_cli list

# 调用技能
python -m robodog.skill_cli move direction=forward speed=0.5 duration=2
python -m robodog.skill_cli run-factory-action action="Shake hand"

# 指定机器人地址
python -m robodog.skill_cli --host 192.168.101.215 get-robot-status
```

### 2. Python API（注册到 LLM 工具）

```python
from robodog.agent_skills import AgentSkills

skills = AgentSkills.connect('192.168.101.215')

# 导出 schema 注册到 LLM 工具列表
schemas = skills.list_skills()

# 调用技能
result = skills.call('move', direction='forward', speed=0.5, duration=2)
result = skills.call('run-factory-action', action='Shake hand')
```

### 3. 新增技能

1. 创建目录 `skills/my-skill/`
2. 编写 `SKILL.md`（frontmatter 中 `name` 需与目录名一致）
3. 编写 `schema.json` 定义参数
4. 编写 `skill.py` 实现 `get_handler(context)`
5. 重新运行即可自动加载，无需修改其他代码

## 安全说明

- 空翻类、前后左右站立类、撒娇、跳跃类动作已被默认过滤
  （`AgentSkills(..., filter_dangerous=False)` 可关闭过滤）
- `set-velocity` 设置后持续生效，必须配合 `stop-movement`
- 机器狗趴下时原厂动作会被机器人拒绝，需先执行 `Recovery stand`
- 连续调用技能建议间隔 2 秒
