---
name: reset-posture
description: 重置机器狗姿态（速度归零、恢复默认身高0.23m和水平姿态）
---

# reset-posture

重置机器狗姿态：速度归零、机体高度恢复默认 0.23m、roll/pitch/yaw 归零。

## 参数

无参数。

## 示例

```bash
python -m robodog.skill_cli reset-posture
```

```python
skills.call('reset-posture')
```
