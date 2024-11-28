# Delayed Dependency Injection in Python

Dependency Container is a Python library that enables a delayed dependency injection approach, allowing you to build your application using an app constructor pattern. It's particularly useful for scenarios where dependencies are defined later in the application lifecycle.

Currently supports [FastAPI](https://fastapi.tiangolo.com/) and [FastStream](https://faststream.airt.ai/latest/).

## Installation

For installation we suggest using [uv](https://github.com/astral-sh/uv):

```bash
uv add dependency-container
```

If you wish to use with `FastStream`:

```bash
uv add "dependency-container[faststream]"
```

Alternatively you can install with `pip`:

```bash
pip install dependency-container
```
