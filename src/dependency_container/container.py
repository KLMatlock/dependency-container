"""Dependency Container for storing and injecting dependencies into the injectable router.

Factory for FastApi routers that inject delayed dependants into actual dependants.
"""

import sys
from abc import ABCMeta
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from inspect import Parameter, Signature, signature
from typing import Annotated, Any, Final, Optional, TypeVar, Union, get_args, get_origin

from fastapi import Depends, params

if sys.version_info >= (3, 10):
    _dataclass_kwargs: Final = {"frozen": True, "slots": True}
else:
    _dataclass_kwargs: Final = {"frozen": True}


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


@dataclass(**_dataclass_kwargs)
class _DelayedDependant:
    attr: str
    source_type: type


def _add_dependency_slots_to_namespace(namespace: dict[str, Any]) -> None:
    """Append the annotations of a class onto the namespace, making it a class variable."""
    annotations: Final[dict[str, Any]] = namespace.get("__annotations__", {})
    for attr_name, attr_type in annotations.items():
        if get_origin(attr_type) != Callable:
            raise TypeError("Receive invalid annotation.")
        # Reannotate the endpoint with attr name for easy lookup later.
        namespace[attr_name] = _DelayedDependant(attr=attr_name, source_type=get_args(attr_type)[1])


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


def _get_delayed_dependent(annotation: type) -> Optional[Union[_DelayedDependant, params.Depends]]:
    """Return the delayed dependent if found in the type annotation."""
    if get_origin(annotation) is not Annotated:
        return None
    annotation_args = get_args(annotation)
    for annotated_value in annotation_args[1:]:
        if isinstance(annotated_value, (_DelayedDependant, params.Depends)):
            return annotated_value
    return None


class DependencyContainer(metaclass=_DependenceContainerMeta):
    """Holds depencies that are to be injected later."""

    def insert_dependency_from_container(self, func: Callable[..., Any]) -> None:
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
                new_param = param.replace(annotation=Annotated[delayed_dependent.source_type, Depends(dependent)])
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
