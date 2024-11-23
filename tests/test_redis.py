"""Test for the redis injector."""

from collections.abc import Callable
from typing import Annotated, Final

import pytest
from faststream.redis import RedisBroker, TestRedisBroker

from dependency_container import DependencyContainer
from dependency_container.faststream.redis import InjectableRedisRouter


class _MyContainer(DependencyContainer):
    x: Callable[..., int]


def _my_dependency() -> int:
    return 5


container: Final = _MyContainer(x=_my_dependency)


@pytest.mark.asyncio
async def test_redis_pubsub():
    """Test that the redis injector works."""
    injector = InjectableRedisRouter()
    called = False
    foo2_called = False

    @injector.publisher("channel2")
    @injector.subscriber("channel1")
    async def channel1_sub(arg1: Annotated[int, _MyContainer.x], msg: str) -> str:
        nonlocal called
        called = True
        assert arg1 == 5
        assert msg == "test"
        return msg

    @injector.subscriber("channel2")
    async def channel2_sub(msg: str) -> None:
        nonlocal foo2_called
        foo2_called = True
        assert msg == "test"

    router = injector.create_router(container)
    broker = RedisBroker()
    broker.include_router(router)

    async with TestRedisBroker(broker) as test_broker:
        await test_broker.publish("test", "channel1")
    assert called
    assert foo2_called


@pytest.mark.asyncio
async def test_redis_subpub():
    """Test that the redis injector works."""
    injector = InjectableRedisRouter()
    called = False
    foo2_called = False

    @injector.subscriber("channel1")
    @injector.publisher("channel2")
    async def channel1_sub(arg1: Annotated[int, _MyContainer.x], msg: str) -> str:
        nonlocal called
        called = True
        assert arg1 == 5
        assert msg == "test"
        return msg

    @injector.subscriber("channel2")
    async def channel2_sub(msg: str) -> None:
        nonlocal foo2_called
        foo2_called = True
        assert msg == "test"

    router = injector.create_router(container)
    broker = RedisBroker()
    broker.include_router(router)

    async with TestRedisBroker(broker) as test_broker:
        await test_broker.publish("test", "channel1")
    assert called
    assert foo2_called
