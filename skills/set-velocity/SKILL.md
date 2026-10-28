---
name: set-velocity
description: 直接设置机器狗线速度和角速度(高级用法)。设置后持续生效，必须配合 stop-movement 使用
---

# set-velocity

直接设置机器狗的三个速度分量，设置后持续生效（不自动停止）。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| vx | number | 是 | 前后速度(m/s)，前为正，范围 -4~4 |
| vy | number | 是 | 左右速度(m/s)，左为正，范围 -1~1 |
| wz | number | 是 | 旋转速度(rad/s)，范围 -2~2 |

## 示例

```bash
python -m robodog.skill_cli set-velocity vx=0.5 vy=0 wz=0
python -m robodog.skill_cli stop-movement
```

```python
skills.call('set-velocity', vx=0.5, vy=0.0, wz=0.0)
skills.call('stop-movement')
```

## 注意事项

- 速度设置后机器人持续运动，**必须调用 `stop-movement` 停止**
- 优先使用 `move` / `turn`（自动停止，更安全）
