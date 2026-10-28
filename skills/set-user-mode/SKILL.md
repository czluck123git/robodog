---
name: set-user-mode
description: 设置机器狗用户模式(normal普通/kids儿童/dance舞蹈/quiet安静/mute静音/extreme运动/long_endurance续航)
---

# set-user-mode

设置机器狗用户模式（不区分大小写）。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| mode | string | 是 | 用户模式：`normal` / `kids` / `dance` / `quiet` / `mute` / `extreme` / `long_endurance` |

## 示例

```bash
python -m robodog.skill_cli set-user-mode mode=dance
```

```python
skills.call('set-user-mode', mode='dance')
```
