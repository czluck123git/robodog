---
name: move
description: 控制机器狗朝指定方向（forward/backward/left/right）移动指定时长，结束后自动停止。用于让机器狗前进、后退、左移或右移
---

# move

控制机器狗朝指定方向移动，指定时长结束后自动停止。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| direction | string | 是 | 移动方向：`forward`(前进) / `backward`(后退) / `left`(左移) / `right`(右移) |
| speed | number | 是 | 移动速度(m/s)，范围 0~2 |
| duration | number | 是 | 移动时长(秒)，范围 0.1~10，结束后自动停止 |

## 示例

```bash
python -m robodog.skill_cli move direction=forward speed=0.5 duration=2
```

```python
skills.call('move', direction='forward', speed=0.5, duration=2)
```

## 注意事项

- 执行前确保机器狗周围有足够空间
- 机器狗趴下时移动无效，需先执行 `run-factory-action` 的 `Recovery stand`
- 连续调用建议间隔 2 秒，等待机器人状态稳定
