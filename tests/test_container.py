"""Tests for Dependency Container Class."""

import inspect
from typing import Annotated, Callable, Final, get_args, get_origin

import pytest
from fastapi import params

from faddi.container import DependencyContainer


def test_dependency_container_inject():
    """Test that the dependency container injects into a annotated function."""

    class MyContainer(DependencyContainer):
        x: Callable[..., int]

    def my_func(
        arg1: Annotated[int, MyContainer.x],
        arg2: int,
        arg3: Annotated[int, "foo"],
        *,
        key: str = "bar",
    ) -> list:
        del arg1, arg2, arg3, key
        return []

    def my_dependency() -> int:
        return 5

    my_container: Final = MyContainer(x=my_dependency)
    my_container.insert_dependency_from_container(my_func)
    new_sig: Final = inspect.signature(my_func)
    new_params: Final = new_sig.parameters

    injected_annotated: Final = new_params["arg1"].annotation
    annotated_args: Final = get_args(injected_annotated)
    noninject_annotated: Final = new_params["arg3"].annotation
    noninject_annotated_args: Final = get_args(noninject_annotated)
    annotation_test: Final[list[bool]] = [
        get_origin(injected_annotated) is Annotated,
        annotated_args[0] is int,
        isinstance(annotated_args[1], params.Depends),
        new_params["arg2"].annotation == int,
        get_origin(noninject_annotated) is Annotated,
        noninject_annotated_args[0] is int,
        noninject_annotated_args[1] == "foo",
        new_params["key"].default == "bar",
        new_sig.return_annotation == list,
    ]
    assert all(annotation_test)


def test_annotation_raises_type_error():
    """Test that passing an invalid dependency value raises an error."""
    with pytest.raises(TypeError):

        class MyContainer(DependencyContainer):
            x: int
