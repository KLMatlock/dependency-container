"""Injectable Router.

Factory for FastApi routers that inject delayed dependants into actual dependants.
"""

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Callable, Final, Generic, TypeVar, Union

from fastapi import APIRouter
from fastapi.params import Depends

from dependency_container.container import DependencyContainer

if sys.version_info >= (3, 10):
    _dataclass_kwargs: Final = {"frozen": True, "slots": True}
else:
    _dataclass_kwargs: Final = {"frozen": True}

F = TypeVar("F", bound=Callable[..., Any])


class _CopySignature(Generic[F]):
    def __init__(self, target: F) -> None:
        pass

    def __call__(self, wrapped: Callable[..., Any]) -> F:
        return wrapped  # type: ignore [reportReturnType]


@dataclass(**_dataclass_kwargs)
class _Route:
    router_method: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    func: Callable[..., Any]


A = TypeVar("A")
B = TypeVar("B")


class InjectableRouter:
    """A router that can be injected with dependencies from a dependency container."""

    @_CopySignature(APIRouter.__init__)
    def __init__(self, dependencies: Union[Sequence[Depends], None] = None, *args: list[Any], **kwargs: dict[str, Any]):
        """Create a new injectable router."""
        self._app_args = args
        self._app_kwargs = kwargs
        self._api_routes: list[_Route] = []
        self._router_dependencies = dependencies

    @_CopySignature(APIRouter.get)
    def get(self, *args: list[Any], **kwargs: dict[str, Any]):  # noqa: ANN201
        """Wrap a GET endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(_Route(APIRouter.get, args, kwargs, func))
            return func

        return decorator

    @_CopySignature(APIRouter.post)
    def post(self, *args: list[Any], **kwargs: dict[str, Any]):  # noqa: ANN201
        """Wrap a POST endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(_Route(APIRouter.post, args, kwargs, func))
            return func

        return decorator

    @_CopySignature(APIRouter.put)
    def put(self, *args: list[Any], **kwargs: dict[str, Any]):  # noqa: ANN201
        """Wrap a PUT endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(_Route(APIRouter.put, args, kwargs, func))
            return func

        return decorator

    @_CopySignature(APIRouter.delete)
    def delete(self, *args: list[Any], **kwargs: dict[str, Any]):  # noqa: ANN201
        """Wrap a DELETE endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(_Route(APIRouter.delete, args, kwargs, func))
            return func

        return decorator

    @_CopySignature(APIRouter.patch)
    def patch(self, *args: list[Any], **kwargs: dict[str, Any]):  # noqa: ANN201
        """Wrap a PATCH endpoint with the router."""

        def decorator(func: Callable[[A], B]) -> Callable[[A], B]:
            self._api_routes.append(_Route(APIRouter.patch, args, kwargs, func))
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
