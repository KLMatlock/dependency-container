"""Contains the Route class."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=False, slots=True)
class Route:
    """Router is a container for a method and its arguments."""

    router_method: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    func: Callable[..., Any]

    def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        """Call the function with the arguments."""
        return self.func(*args, **kwargs)
