"""Dependency Container for FastStream Redis client."""

from collections.abc import Callable
from typing import Any, Final, TypeVar

from faststream.redis import RedisRouter

from dependency_container.container import DependencyContainer, DependencySource
from dependency_container.route import Route
from dependency_container.signature import CopySignature

A = TypeVar("A")
B = TypeVar("B")


class InjectableRedisRouter:
    """A wrapper for a Redis Router that allows for runtime injection."""

    @CopySignature(RedisRouter.__init__)
    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]):
        """Create a new injectable router."""
        self._router_args = args
        self._router_kwargs = kwargs
        self._routes: list[Route] = []

    @CopySignature(RedisRouter.subscriber)
    def subscriber(self, *args: list[Any], **kwargs: dict[str, Any]):  # noqa: ANN201
        """Wrap a subscriber with the router."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._routes.append(Route(RedisRouter.subscriber, args, kwargs, func))
            return func

        return decorator

    @CopySignature(RedisRouter.publisher)
    def publisher(self, *args: list[Any], **kwargs: dict[str, Any]):  # noqa: ANN201
        """Wrap a publisher with the router."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._routes.append(Route(RedisRouter.publisher, args, kwargs, func))
            return func

        return decorator

    def create_router(self, container: DependencyContainer) -> RedisRouter:
        """Create a router with dependencies injected from the container."""
        router: Final = RedisRouter(*self._router_args, **self._router_kwargs)
        for route in self._routes:
            container.insert_dependency_from_container(route.func, source=DependencySource.FASTSTREAM)
            route_wrapper = route.router_method(router, *route.args, **route.kwargs)
            route_wrapper(route.func)

        return router
