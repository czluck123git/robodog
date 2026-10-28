"""机器狗原厂动作接口

通过 rosbridge 与机器人的 /alphadog_node/do_action action server 通信，
发送原厂内置动作（坐下、趴下、跳跃、翻滚、握手、舞蹈等）。
"""
import threading
import uuid
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import roslibpy

# actionlib GoalStatus 状态码 -> 文本
GOAL_STATUS_TEXT = {
    0: 'PENDING',
    1: 'ACTIVE',
    2: 'PREEMPTED',
    3: 'SUCCEEDED',
    4: 'ABORTED',
    5: 'REJECTED',
    6: 'PREEMPTING',
    7: 'RECALLING',
    8: 'RECALLED',
    9: 'LOST',
}

# 默认过滤掉的动作类别：空翻类、前后左右站立类、撒娇、跳跃类
EXCLUDED_ACTIONS = frozenset({
    'Back flip', 'Front flip', 'Left flip', 'Right flip',
    'Back stand', 'Front stand', 'Left stand', 'Right stand',
    'Coax',
    'Jump', 'Jump round', 'Jump forward',
})


@dataclass
class FactoryAction:
    """原厂动作定义"""
    action_id: int
    name: str


class FactoryActions:
    """原厂动作执行器

    使用已连接的 roslibpy.Ros 客户端，通过 ROS action 协议
    向 /alphadog_node/do_action 发送动作目标并等待结果。
    """

    GOAL_TOPIC = '/alphadog_node/do_action/goal'
    RESULT_TOPIC = '/alphadog_node/do_action/result'
    FEEDBACK_TOPIC = '/alphadog_node/do_action/feedback'
    CANCEL_TOPIC = '/alphadog_node/do_action/cancel'
    AVAILABLE_TOPIC = '/alphadog_node/available_actions'

    GOAL_TYPE = 'ros_alphadog/DoActionGoal'
    RESULT_TYPE = 'ros_alphadog/DoActionResult'
    FEEDBACK_TYPE = 'ros_alphadog/DoActionFeedback'
    CANCEL_TYPE = 'actionlib_msgs/GoalID'
    AVAILABLE_TYPE = 'ros_alphadog/AvailableActions'

    def __init__(self, ros_client: 'roslibpy.Ros'):
        """参数:
            ros_client: 已连接的 roslibpy.Ros 实例
        """
        self._client = ros_client
        self._lock = threading.Lock()
        self._goal_id: Optional[str] = None
        self._done = threading.Event()
        self._result: Optional[dict] = None

    @property
    def is_executing(self) -> bool:
        """是否有动作正在执行"""
        with self._lock:
            return self._goal_id is not None

    def get_available_actions(self, timeout: float = 5.0) -> List[FactoryAction]:
        """获取机器人当前可用的原厂动作列表"""
        received = threading.Event()
        holder = {}

        topic = roslibpy.Topic(self._client, self.AVAILABLE_TOPIC, self.AVAILABLE_TYPE)

        def callback(msg):
            if not received.is_set():
                holder['msg'] = msg
                received.set()

        topic.subscribe(callback)
        try:
            if not received.wait(timeout):
                raise TimeoutError(f'获取动作列表超时 ({timeout}s)，话题 {self.AVAILABLE_TOPIC} 无数据')
        finally:
            topic.unsubscribe()

        msg = holder['msg']
        return [
            FactoryAction(action_id=int(aid), name=str(name))
            for aid, name in zip(msg.get('action_id', []), msg.get('action_name', []))
        ]

    def run_action(
        self,
        action_id: int,
        timeout: Optional[float] = None,
        feedback_cb: Optional[Callable[[float], None]] = None,
    ) -> Tuple[int, str]:
        """执行原厂动作并等待结束

        参数:
            action_id: 动作ID（见 /alphadog_node/available_actions）
            timeout: 最长等待时间(秒)，None表示无限等待
            feedback_cb: 进度回调，参数为0~1的进度值

        返回:
            (result_code, status_text): result_code为0表示成功，
            status_text为动作结束状态描述
        """
        with self._lock:
            if self._goal_id is not None:
                raise RuntimeError('已有动作正在执行，请先停止或等待其完成')
            goal_id = str(uuid.uuid4())
            self._goal_id = goal_id
            self._done.clear()
            self._result = None

            result_sub = roslibpy.Topic(self._client, self.RESULT_TOPIC, self.RESULT_TYPE)
            feedback_sub = roslibpy.Topic(self._client, self.FEEDBACK_TOPIC, self.FEEDBACK_TYPE)

            def on_result(msg):
                status = msg.get('status', {})
                if status.get('goal_id', {}).get('id') == goal_id:
                    self._result = msg
                    self._done.set()

            def on_feedback(msg):
                if msg.get('status', {}).get('goal_id', {}).get('id') == goal_id:
                    progress = msg.get('feedback', {}).get('progress', 0.0)
                    if feedback_cb:
                        try:
                            feedback_cb(float(progress))
                        except Exception:
                            pass

            result_sub.subscribe(on_result)
            feedback_sub.subscribe(on_feedback)

            goal_topic = roslibpy.Topic(self._client, self.GOAL_TOPIC, self.GOAL_TYPE)
            goal_topic.publish({
                'header': {'seq': 0, 'stamp': {'secs': 0, 'nsecs': 0}, 'frame_id': ''},
                'goal_id': {'stamp': {'secs': 0, 'nsecs': 0}, 'id': goal_id},
                'goal': {'action_id': int(action_id)},
            })
            goal_topic.unadvertise()

        try:
            completed = self._done.wait(timeout)
            if not completed or self._result is None:
                raise TimeoutError(f'动作执行超时 ({timeout}s) 或未收到结果')

            status = self._result.get('status', {})
            status_code = int(status.get('status', 9))
            status_text = GOAL_STATUS_TEXT.get(status_code, f'UNKNOWN({status_code})')
            result_code = int(self._result.get('result', {}).get('result', 1))
            return result_code, status_text
        finally:
            result_sub.unsubscribe()
            feedback_sub.unsubscribe()
            with self._lock:
                self._goal_id = None

    def cancel(self) -> bool:
        """取消当前正在执行的动作，返回是否发送了取消请求"""
        with self._lock:
            goal_id = self._goal_id
        if not goal_id:
            return False

        cancel_topic = roslibpy.Topic(self._client, self.CANCEL_TOPIC, self.CANCEL_TYPE)
        cancel_topic.publish({'stamp': {'secs': 0, 'nsecs': 0}, 'id': goal_id})
        cancel_topic.unadvertise()
        return True
