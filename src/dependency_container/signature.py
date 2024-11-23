"""Function for copying the signature of another function."""

from collections.abc import Callable
from typing import Any, Generic, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class CopySignature(Generic[F]):
    """Copy the signature of another function."""

    def __init__(self, target: F) -> None:  # noqa: D107
        pass

    def __call__(self, wrapped: Callable[..., Any]) -> F:  # noqa: D102
        return wrapped  # type: ignore [reportReturnType]
