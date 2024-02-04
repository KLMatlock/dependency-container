"""Tests for the InjectableRouter class."""

from collections.abc import Callable
from typing import Annotated, Final

from fastapi import FastAPI
from fastapi.testclient import TestClient

from faddi import DependencyContainer, InjectableRouter


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
