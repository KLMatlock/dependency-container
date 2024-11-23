"""Injectable Router.

Factory for FastApi routers that inject delayed dependants into actual dependants.
"""

from collections.abc import Callable, Sequence
from typing import Any, Final, TypeVar

from fastapi import APIRouter
from fastapi.params import Depends

from dependency_container.container import DependencyContainer
from dependency_container.route import Route
from dependency_container.signature import CopySignature

A = TypeVar("A")
B = TypeVar("B")


class InjectableRouter:
    """A router that can be injected with dependencies from a dependency container."""

    @CopySignature(APIRouter.__init__)
    def __init__(self, dependencies: Sequence[Depends] | None = None, *args: list[Any], **kwargs: Any):
        """Create a new injectable router."""
        self._app_args = args
        self._app_kwargs = kwargs
        self._api_routes: list[Route] = []
        self._router_dependencies = dependencies

    @CopySignature(APIRouter.get)
    def get(self, *args: list[Any], **kwargs: Any):  # noqa: ANN201
        """Wrap a GET endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(Route(APIRouter.get, args, kwargs, func))
            return func

        return decorator

    @CopySignature(APIRouter.post)
    def post(self, *args: list[Any], **kwargs: Any):  # noqa: ANN201
        """Wrap a POST endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(Route(APIRouter.post, args, kwargs, func))
            return func

        return decorator

    @CopySignature(APIRouter.put)
    def put(self, *args: list[Any], **kwargs: Any):  # noqa: ANN201
        """Wrap a PUT endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(Route(APIRouter.put, args, kwargs, func))
            return func

        return decorator

    @CopySignature(APIRouter.delete)
    def delete(self, *args: list[Any], **kwargs: Any):  # noqa: ANN201
        """Wrap a DELETE endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(Route(APIRouter.delete, args, kwargs, func))
            return func

        return decorator

    @CopySignature(APIRouter.patch)
    def patch(self, *args: list[Any], **kwargs: Any):  # noqa: ANN201
        """Wrap a PATCH endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(Route(APIRouter.patch, args, kwargs, func))
            return func

        return decorator

    def create_router(self, container: DependencyContainer) -> APIRouter:
        """Create a router with dependencies injected from the container."""
        new_dependencies = self._router_dependencies
        if new_dependencies is not None:
            new_dependencies = container.create_dependency_sequence(new_dependencies)
        router: Final = APIRouter(*self._app_args, dependencies=new_dependencies, **self._app_kwargs)
        for route in self._api_routes:
            container.insert_dependency_from_container(route.func)
            route_wrapper = route.router_method(router, *route.args, **route.kwargs)
            route_wrapper(route.func)

        return router
