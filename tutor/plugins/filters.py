# TODO should we really keep this module (and actions) inside plugins? After all
# we also use this to extend config, env, and sorts of stuff.
import typing as t

from tutor import fmt

from . import contexts

# For now, this signature is not very restrictive. In the future, we could improve it by writing:
#
# P = ParamSpec("P")
# CallableFilter = t.Callable[Concatenate[T, P], T]
#
# See PEP-612: https://www.python.org/dev/peps/pep-0612/
# Unfortunately, this piece of code fails because of a bug in mypy:
# https://github.com/python/mypy/issues/11833
# https://github.com/python/mypy/issues/8645
# https://github.com/python/mypy/issues/5876
# https://github.com/python/typing/issues/696
T = t.TypeVar("T")
CallableFilter = t.Callable[..., t.Any]


# TODO the list of filters should be hardcoded as static variables in a separate
# module and documented (same for actions)


class Filter(contexts.Contextualized):
    """
    TODO document this class.
    """

    def __init__(self, func: CallableFilter):
        super().__init__()
        self.func = func

    def apply(
        self, value: T, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
    ) -> T:
        if self.is_in_context(context):
            value = self.func(value, *args, **kwargs)
        return value


class Filters:
    """
    Singleton set of named filters.
    """

    INSTANCE = None

    @classmethod
    def instance(cls) -> "Filters":
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
        return cls.INSTANCE

    def __init__(self) -> None:
        self.filters: t.Dict[str, t.List[Filter]] = {}

    def add(self, name: str, func: CallableFilter) -> None:
        self.filters.setdefault(name, []).append(Filter(func))

    def apply(
        self,
        name: str,
        value: T,
        *args: t.Any,
        context: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> T:
        """
        Apply all declared filters to a single value, passing along the additional arguments.

        TODO document context
        """
        for filtre in self.filters.get(name, []):
            try:
                value = filtre.apply(value, *args, context=context, **kwargs)
            except:
                fmt.echo_error(f"Error applying {filtre.func} in filter '{name}'")
                raise
        return value

    def clear_all(self, context: t.Optional[str] = None) -> None:
        """
        Clear any previously defined filter with the  given context.
        """
        for name in self.filters:
            self.clear(name, context=context)

    def clear(self, name: str, context: t.Optional[str] = None) -> None:
        """
        Clear any previously defined filter with the given name and context.
        """
        if name not in self.filters:
            return
        self.filters[name] = [
            filtre for filtre in self.filters[name] if not filtre.is_in_context(context)
        ]


def add(name: str) -> t.Callable[[CallableFilter], CallableFilter]:
    """
    Decorator for functions that will be applied to a single named filter.

    The return value of each filter function will be passed as the first argument of the next one.

    Usage:

        @filters.add("my-filter")
        def my_func(value, some_other_arg):
            # Do something with `value`
            ...
            return value

    TODO use python decorator to make it easier to troubleshoot on error
    """

    def inner(func: CallableFilter) -> CallableFilter:
        Filters.instance().add(name, func)
        return func

    return inner


def add_item(name: str, item: T) -> None:
    """
    TODO explain me
    """
    add_items(name, [item])


def add_items(name: str, items: t.List[T]) -> None:
    """
    TODO explain me
    """

    @add(name)
    def callback(value: t.List[T], *_args: t.Any, **_kwargs: t.Any) -> t.List[T]:
        return value + items


apply = Filters.instance().apply
clear = Filters.instance().clear
clear_all = Filters.instance().clear_all
