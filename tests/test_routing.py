"""Tests for the InjectableRouter class."""

from collections.abc import Callable
from typing import Annotated, Final

from dependency_container import DependencyContainer, InjectableRouter
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class _MyContainer(DependencyContainer):
    x: Callable[..., int]


def _my_dependency() -> int:
    return 5


container: Final = _MyContainer(x=_my_dependency)


def create_test_client(router: InjectableRouter) -> TestClient:
    """Create a test client with the given router."""
    api_router: Final = router.create_router(container)
    app: Final = FastAPI()
    app.include_router(api_router)
    return TestClient(app)


def test_router_get():
    """Test injecting in router GET."""
    router: Final = InjectableRouter(prefix="/api")

    @router.get("/foo")
    def foo(arg1: Annotated[int, _MyContainer.x]) -> int:
        return arg1

    test_client: Final = create_test_client(router)
    res: Final = test_client.get("/api/foo")
    assert all([res.status_code == 200, res.json() == 5])


def test_router_post():
    """Test injecting in router POST."""
    router: Final = InjectableRouter(prefix="/api")

    @router.post("/foo")
    def foo(arg1: Annotated[int, _MyContainer.x]) -> int:
        return arg1

    test_client: Final = create_test_client(router)
    res: Final = test_client.post("/api/foo")
    assert all([res.status_code == 200, res.json() == 5])


def test_router_put():
    """Test injecting in router PUT."""
    router: Final = InjectableRouter(prefix="/api")

    @router.put("/foo")
    def foo(arg1: Annotated[int, _MyContainer.x]) -> int:
        return arg1

    test_client: Final = create_test_client(router)
    res: Final = test_client.put("/api/foo")
    assert all([res.status_code == 200, res.json() == 5])


def test_router_patch():
    """Test injecting in router PATCH."""
    router: Final = InjectableRouter(prefix="/api")

    @router.patch("/foo")
    def foo(arg1: Annotated[int, _MyContainer.x]) -> int:
        return arg1

    test_client: Final = create_test_client(router)
    res: Final = test_client.patch("/api/foo")
    assert all([res.status_code == 200, res.json() == 5])


def test_router_delete():
    """Test injecting in router DELETE."""
    router: Final = InjectableRouter(prefix="/api")

    @router.delete("/foo")
    def foo(arg1: Annotated[int, _MyContainer.x]) -> int:
        return arg1

    test_client: Final = create_test_client(router)
    res: Final = test_client.delete("/api/foo")
    assert all([res.status_code == 200, res.json() == 5])


def test_router_dependency():
    """Test injecting router based dependencies."""

    class _SequenceContainer(DependencyContainer):
        x: Callable[..., None]

    noninject_called = False

    def _non_injected_dependency() -> None:
        nonlocal noninject_called
        noninject_called = True

    router: Final = InjectableRouter(
        prefix="/api",
        dependencies=[Depends(_SequenceContainer.x), Depends(_non_injected_dependency)],
    )

    @router.get("/foo")
    def foo() -> int:
        return 5

    called = False

    def _my_dependency() -> None:
        nonlocal called
        called = True

    container: Final = _SequenceContainer(x=_my_dependency)
    api_router: Final = router.create_router(container)
    app: Final = FastAPI()
    app.include_router(api_router)
    test_client: Final = TestClient(app)

    res: Final = test_client.get("/api/foo")
    assert all(
        [
            called,
            noninject_called,
            res.status_code == 200,
        ],
    )


def test_router_dependency_recursive():
    """Test injecting router based dependencies with recursive dependencies."""

    class _SequenceContainer(DependencyContainer):
        x: Callable[..., int]

    injected_called = False

    def _injected_dependency() -> int:
        nonlocal injected_called
        injected_called = True
        return 5

    def _normal_dependency(arg1: Annotated[int, _SequenceContainer.x]) -> int:
        return arg1

    router: Final = InjectableRouter(
        prefix="/api",
        dependencies=[Depends(_normal_dependency)],
    )

    @router.get("/foo")
    def foo() -> int:
        return 5

    container: Final = _SequenceContainer(x=_injected_dependency)
    api_router: Final = router.create_router(container)
    app: Final = FastAPI()
    app.include_router(api_router)
    test_client: Final = TestClient(app)

    test_client.get("/api/foo")
    assert injected_called, "Did not injected dependency."
