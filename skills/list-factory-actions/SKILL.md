---
name: list-factory-actions
description: 获取机器人当前可用的原厂动作列表（如 Shake hand握手、Sit down坐下、Sway摇摆、Dynamic dance动态舞蹈），执行前应先调用此skill查询
---

# list-factory-actions

获取机器人当前可用的原厂动作列表。危险动作（空翻/前后左右站立/撒娇/跳跃）已被过滤，不在列表中。

## 参数

无参数。

## 返回

`data` 字段为动作数组，每项包含 `id` 和 `name`。

## 示例

```bash
python -m robodog.skill_cli list-factory-actions
```

```python
result = skills.call('list-factory-actions')
print(result['data'])   # [{'id': 514, 'name': 'Shake hand'}, ...]
```
