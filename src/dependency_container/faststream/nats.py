"""Dependency Container for FastStream Redis client."""

from collections.abc import Callable, Iterable
from typing import Any, Final, TypeVar

from faststream.broker.wrapper.call import HandlerCallWrapper
from faststream.nats import NatsRoute, NatsRouter

from dependency_container.container import DependencyContainer, DependencySource
from dependency_container.route import Route
from dependency_container.signature import CopySignature

A = TypeVar("A")
B = TypeVar("B")


class InjectableNatsRouter:
    """A wrapper for a Redis Router that allows for runtime injection."""

    __slots__ = ("_handlers", "_prefix", "_router_kwargs", "_routes")

    @CopySignature(NatsRouter.__init__)
    def __init__(self, prefix: str = "", handlers: Iterable[NatsRoute] = (), **kwargs: Any):
        """Create a new injectable router."""
        self._prefix = prefix
        self._handlers = handlers
        self._router_kwargs = kwargs
        self._routes: list[Route] = []

    @CopySignature(NatsRouter.subscriber)
    def subscriber(self, *args: list[Any], **kwargs: Any):  # noqa: ANN201
        """Wrap a subscriber with the router."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            route = Route(NatsRouter.subscriber, args, kwargs, func)
            self._routes.append(route)
            return route

        return decorator

    @CopySignature(NatsRouter.publisher)
    def publisher(self, *args: list[Any], **kwargs: Any):  # noqa: ANN201
        """Wrap a publisher with the router."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            route = Route(NatsRouter.publisher, args, kwargs, func)
            self._routes.append(route)
            return route

        return decorator

    def create_router(self, container: DependencyContainer) -> NatsRouter:
        """Create a router with dependencies injected from the container."""
        router: Final = NatsRouter(self._prefix, self._handlers, **self._router_kwargs)
        for route in self._routes:
            func = route.get_func()
            if not isinstance(func, HandlerCallWrapper):
                container.insert_dependency_from_container(func, source=DependencySource.FASTSTREAM)
            route_wrapper = route.router_method(router, *route.args, **route.kwargs)
            route.func = route_wrapper(func)

        return router
