"""FastApi Delayed Dependency Injection package.

Support delayed dependency injection in FastApi to enable app constructor pattern.
"""

from dependency_container.container import DependencyContainer
from dependency_container.routing import InjectableRouter

__all__: list[str] = ["DependencyContainer", "InjectableRouter"]
__version__ = "0.1.0"
