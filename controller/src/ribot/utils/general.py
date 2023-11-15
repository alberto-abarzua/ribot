import functools
import inspect
from typing import Any, Callable, TypeVar

# Define a generic type variable for instance methods
T = TypeVar("T", bound=Callable[..., Any])


def no_self_call(func: T) -> T:
    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        current_frame = inspect.currentframe()
        if current_frame is None:
            raise ValueError("Cannot get current frame")

        caller_frame = current_frame.f_back
        if caller_frame is None:
            raise ValueError("Cannot get caller frame")

        caller_self = caller_frame.f_locals.get("self", None)

        if caller_self is self:
            raise ValueError(f"{func.__name__} cannot be called by another method of the same object")

        return func(self, *args, **kwargs)

    return wrapper  # type: ignore
