"""Contains the Route class."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Union


@dataclass(frozen=False, slots=True)
class Route:
    """Router is a container for a method and its arguments."""

    router_method: Callable[..., Callable[[Callable[..., Any]], Any]]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    func: Union[Callable[..., Any], "Route"]

    def get_func(self) -> Callable[..., Any]:
        """Get the function from the route."""
        if isinstance(self.func, Route):
            return self.func.get_func()
        return self.func

    def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        """Call the function with the arguments."""
        return self.func(*args, **kwargs)
