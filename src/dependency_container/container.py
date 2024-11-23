"""Dependency Container for storing and injecting dependencies into the injectable router.

Factory for FastApi routers that inject delayed dependants into actual dependants.
"""

import sys
from abc import ABCMeta
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from inspect import Parameter, Signature, signature
from typing import Annotated, Any, Final, TypeVar, get_args, get_origin

from fastapi import Depends, params


class DependencySource(Enum):
    """Enumeration for the source of a dependency."""

    FASTAPI = "FastAPI"
    FASTSTREAM = "FastStream"


if sys.version_info >= (3, 11):
    from typing import dataclass_transform
else:
    C = TypeVar("C")

    def dataclass_transform(*args: list[Any], **kwargs: dict[str, Any]) -> Callable[[C], C]:
        """Placeholder if dataclass transform is not found."""
        del args
        del kwargs

        def decorator(cls_or_fn: C) -> C:
            return cls_or_fn

        return decorator


@dataclass(frozen=True, slots=True)
class _DelayedDependant:
    attr: str
    source_type: type


def _get_dependent_source(dependent_origin: type | None) -> type:
    """Get the source type of a dependent."""
    if isinstance(dependent_origin, Callable):
        return get_args(dependent_origin)[1]
    if dependent_origin is None:
        raise TypeError(f"Dependant origin {dependent_origin} is not a valid type.")

    return dependent_origin


def _add_dependency_slots_to_namespace(namespace: dict[str, Any]) -> None:
    """Append the annotations of a class onto the namespace, making it a class variable."""
    annotations: Final[dict[str, Any]] = namespace.get("__annotations__", {})
    for attr_name, attr_type in annotations.items():
        source_type = _get_dependent_source(attr_type)
        # Reannotate the endpoint with attr name for easy lookup later.
        namespace[attr_name] = _DelayedDependant(attr=attr_name, source_type=source_type)


@dataclass_transform(kw_only_default=True)
class _DependenceContainerMeta(ABCMeta):
    """Metaclass for creating dependency containers."""

    def __new__(
        cls,
        cls_name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, Any],
    ) -> type:
        _add_dependency_slots_to_namespace(namespace)
        base_cls = super().__new__(cls, cls_name, bases, namespace)
        return dataclass(base_cls)


def _get_delayed_dependent(annotation: type) -> _DelayedDependant | params.Depends | None:
    """Return the delayed dependent if found in the type annotation."""
    if get_origin(annotation) is not Annotated:
        return None
    annotation_args = get_args(annotation)
    for annotated_value in annotation_args[1:]:
        if isinstance(annotated_value, _DelayedDependant | params.Depends):
            return annotated_value
    return None


class DependencyContainer(metaclass=_DependenceContainerMeta):
    """Holds depencies that are to be injected later."""

    def insert_dependency_from_container(
        self, func: Callable[..., Any], source: DependencySource = DependencySource.FASTAPI
    ) -> None:
        """Insert an annotated dependency from the container.

        Parameters
        ----------
        func: Callable
            The function to insert the dependency into. This function will be modified in place.
        """
        merged_params: Final[list[Parameter]] = []
        func_sig: Final = signature(func)

        # Go through each parameter and replace ones annotated with injected values to new ones.
        for param in func_sig.parameters.values():
            new_param: Parameter = param
            delayed_dependent = _get_delayed_dependent(param.annotation)
            if isinstance(delayed_dependent, _DelayedDependant):
                dependent: Callable[..., Any] = getattr(self, delayed_dependent.attr)
                # TODO: Get original annotation.
                if source == DependencySource.FASTAPI:
                    depends_annotate = Depends(dependent)
                elif source == DependencySource.FASTSTREAM:
                    from faststream import Depends as FastStreamDepends

                    depends_annotate = FastStreamDepends(dependent)
                new_param = param.replace(annotation=Annotated[delayed_dependent.source_type, depends_annotate])
            elif isinstance(delayed_dependent, params.Depends) and delayed_dependent.dependency:
                dependent: Callable[..., Any] = delayed_dependent.dependency
                self.insert_dependency_from_container(dependent)
            merged_params.append(new_param)
        func.__signature__ = Signature(parameters=merged_params, return_annotation=func_sig.return_annotation)  # type: ignore [reportFunctionMemberAccess]

    def create_dependency_sequence(self, dependencies: Sequence[params.Depends]) -> Sequence[params.Depends]:
        """Iterate through a sequence of dependencies and create the realized values."""
        new_dependencies: Final[Sequence[params.Depends]] = []
        for dependency in dependencies:
            wrapped_dependency = dependency.dependency
            if isinstance(wrapped_dependency, _DelayedDependant):
                new_dependency = Depends(getattr(self, wrapped_dependency.attr))
                new_dependencies.append(new_dependency)
            elif wrapped_dependency:
                self.insert_dependency_from_container(wrapped_dependency)
                new_dependencies.append(dependency)
            else:
                new_dependencies.append(dependency)

        return new_dependencies
