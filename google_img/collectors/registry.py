from typing import Any, Callable, Optional


def make_registry() -> Callable[..., Callable[..., Any]]:
    registry = {}

    def registrar(
        function: Optional[Callable[..., Any]] = None, name: str = ""
    ) -> Callable[..., Any]:
        def wrapper(func_: Callable[..., Any]) -> Callable[..., Any]:
            registry[name] = func_
            return func_

        if function is not None:
            return wrapper(function)
        return wrapper

    registrar.registry = registry
    return registrar


collector = make_registry()
