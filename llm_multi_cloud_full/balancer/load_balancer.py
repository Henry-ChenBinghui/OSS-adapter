import threading
from collections import defaultdict

class RoundRobinBalancer:
    def __init__(self):
        self._index = defaultdict(int)
        self._lock = threading.Lock()

    def select(self, key: str, options: list):
        with self._lock:
            idx = self._index[key]
            self._index[key] = (idx + 1) % len(options)
        return options[idx]
