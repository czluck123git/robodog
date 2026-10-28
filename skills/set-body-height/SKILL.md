---
name: set-body-height
description: 设置机器狗机体高度(0.09~0.35米)
---

# set-body-height

设置机器狗机体高度。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| height_m | number | 是 | 机体高度(米)，范围 0.09~0.35 |

## 示例

```bash
python -m robodog.skill_cli set-body-height height_m=0.3
```

```python
skills.call('set-body-height', height_m=0.3)
```
