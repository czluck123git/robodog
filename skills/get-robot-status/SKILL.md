---
name: get-robot-status
description: 获取机器狗当前状态，包括用户模式、站立状态、位置、姿态角和速度
---

# get-robot-status

获取机器狗当前状态：用户模式、estop/错误标志、站立状态、位置、姿态角、速度。

## 参数

无参数。

## 返回

`data` 字段包含:

| 字段 | 说明 |
|---|---|
| user_mode | 用户模式 (NORMAL/KIDS/DANCE 等) |
| standing | 是否站立 |
| estop | 是否急停状态 |
| error | 是否有错误 |
| position | 位置 x/y/z (米) |
| rpy | 姿态角 roll/pitch/yaw (弧度) |
| velocity | 速度 vx/vy/wz |
| state_valid | 状态数据是否有效（刚连接时可能为false，等待2秒再查） |

## 示例

```bash
python -m robodog.skill_cli get-robot-status
```

```python
skills.call('get-robot-status')
```
