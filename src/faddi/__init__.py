"""FastApi Delayed Dependency Injection package.

Support delayed dependency injection in FastApi to enable app constructor pattern.
"""

from faddi.container import DependencyContainer
from faddi.routing import InjectableRouter

__all__: list[str] = ["DependencyContainer", "InjectableRouter"]
