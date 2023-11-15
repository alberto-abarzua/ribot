import queue
import threading
import types
from typing import Optional, Type


class FIFOLock:
    def __init__(self) -> None:
        self.internal_lock: threading.Lock = threading.Lock()
        self.queue: queue.Queue = queue.Queue()
        self.current_owner: Optional[int] = None

    def acquire(self) -> None:
        current_thread: int = threading.get_ident()
        self.queue.put(current_thread)
        while self.queue.queue[0] != current_thread or not self.internal_lock.acquire(False):
            pass
        self.current_owner = current_thread

    def release(self) -> None:
        self.internal_lock.release()
        self.queue.get()

    def __enter__(self) -> None:
        self.acquire()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        self.release()
