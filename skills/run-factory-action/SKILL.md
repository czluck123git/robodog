---
name: run-factory-action
description: 执行机器人原厂内置动作（如 Shake hand握手、Sit down坐下、Recovery stand恢复站立、Sway摇摆、Dynamic dance动态舞蹈）。执行完成或出错后返回，可用 cancel-factory-action 中途取消。机器狗趴下时大部分动作会被拒绝，需先执行 Recovery stand
---

# run-factory-action

执行机器人原厂内置动作并等待结束。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| action | string | 是 | 动作名称或ID，如 `Shake hand`、`Sit down` 或 `514`。支持唯一前缀（如 `sit` 匹配 `Sit down`） |
| timeout | number | 否 | 最长等待时间(秒)，默认 60，范围 1~300 |

## 示例

```bash
python -m robodog.skill_cli run-factory-action action=Shake_hand
```

```python
skills.call('run-factory-action', action='Shake hand')
skills.call('run-factory-action', action='514')
```

## 注意事项

- 执行前建议先调用 `list-factory-actions` 确认动作可用
- 机器狗趴下时动作会被机器人拒绝（返回 result=3 ABORTED），需先执行 `Recovery stand`
- 动作执行过程中请勿触碰机器狗
- 连续执行动作建议间隔 2 秒，等待机器人状态稳定
