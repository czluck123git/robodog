---
name: stop-movement
description: 停止机器狗所有运动（线速度和角速度归零）。配合 set-velocity 使用，或随时用于急停
---

# stop-movement

机器狗所有运动停止（vx/vy/wz 归零）。

## 参数

无参数。

## 示例

```bash
python -m robodog.skill_cli stop-movement
```

```python
skills.call('stop-movement')
```
