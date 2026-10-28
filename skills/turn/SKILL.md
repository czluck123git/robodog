---
name: turn
description: 控制机器狗原地向左/右转向指定时长，结束后自动停止
---

# turn

控制机器狗原地转向，指定时长结束后自动停止。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| direction | string | 是 | 转向方向：`left`(左转) / `right`(右转) |
| speed | number | 是 | 转向速度(rad/s)，范围 0.1~2 |
| duration | number | 是 | 转向时长(秒)，范围 0.1~10，结束后自动停止 |

## 示例

```bash
python -m robodog.skill_cli turn direction=left speed=1.0 duration=1
```

```python
skills.call('turn', direction='left', speed=1.0, duration=1)
```

## 注意事项

- 执行前确保机器狗周围有足够空间
- 机器狗趴下时转向无效，需先执行 `run-factory-action` 的 `Recovery stand`
