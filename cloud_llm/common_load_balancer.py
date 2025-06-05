import threading
from abc import abstractmethod, ABC
from collections import defaultdict
from typing import Optional, List

# 这里定义最小依赖的类型，实际项目可从cloud_llm/types.py import
class LlmStatus:
    INACTIVE = 0
    ACTIVE = 1

class LlmInstanceEntry:
    def __init__(self, client, instance=None, status=LlmStatus.ACTIVE):
        self.client = client
        self.instance = instance
        self.status = status

class LoadBalancer(ABC):
    @staticmethod
    def _get_index_key(entry: LlmInstanceEntry):
        return str(id(entry))

    def __init__(self, max_iteration: int = 1000):
        self._index = defaultdict(int)
        self._index_lock = threading.Lock()
        self._max_iteration = max_iteration

    @staticmethod
    def create(strategy: str) -> "LoadBalancer":
        if strategy == "master-slave":
            return MasterSlaveLoadBalancer()
        elif strategy == "round-robin":
            return RoundRobinLoadBalancer()
        else:
            raise Exception(f"{strategy} load balancer strategy not supported.")

    def cycle(self, options: List[LlmInstanceEntry]) -> LlmInstanceEntry:
        entry = options[0]
        key = self._get_index_key(entry)
        count = 0
        while self._index[key] < len(options):
            count += 1
            if count > self._max_iteration:
                raise RuntimeError("Exceeded maximum iteration limit for load balancing.")
            entry = self._get(options, key=key)
            with self._index_lock:
                self._index[key] = (self._index[key] + 1) % len(options)
            if entry.status != LlmStatus.INACTIVE:
                return entry
        with self._index_lock:
            self._index[key] = 0
        raise RuntimeError("Could not find an active endpoint for balancing.")

    @abstractmethod
    def _get(self, options: List[LlmInstanceEntry], key: str = None) -> LlmInstanceEntry:
        raise NotImplementedError()

class MasterSlaveLoadBalancer(LoadBalancer):
    def _get(self, options: List[LlmInstanceEntry], key: str = None) -> LlmInstanceEntry:
        if key is None:
            key = self._get_index_key(options[0])
        options_sorted = sorted(options, key=lambda ep: getattr(ep.instance, 'type', 0))
        return options_sorted[self._index[key]]

class RoundRobinLoadBalancer(LoadBalancer):
    def _get(self, options: List[LlmInstanceEntry], key: str = None) -> LlmInstanceEntry:
        if key is None:
            key = self._get_index_key(options[0])
        return options[self._index[key]] 