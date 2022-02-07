import typing as t

from . import contexts

# Similarly to CallableFilter, it should be possible to refine the definition of
# CallableAction in the future.
CallableAction = t.Callable[..., None]


class Action(contexts.Contextualized):
    def __init__(self, func: CallableAction):
        super().__init__()
        self.func = func

    def do(
        self, *args: t.Any, context: t.Optional[str] = None, **kwargs: t.Any
    ) -> None:
        if self.is_in_context(context):
            self.func(*args, **kwargs)


class Actions:
    """
    Singleton set of named actions.
    """

    INSTANCE = None

    @classmethod
    def instance(cls) -> "Actions":
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
        return cls.INSTANCE

    def __init__(self) -> None:
        self.actions: t.Dict[str, t.List[Action]] = {}

    def add(self, name: str, func: CallableAction) -> None:
        self.actions.setdefault(name, []).append(Action(func))

    def do(self, name: str, *args: t.Any, **kwargs: t.Any) -> None:
        for action in self.actions.get(name, []):
            action.do(*args, **kwargs)

    def clear_all(self, context: t.Optional[str] = None) -> None:
        """
        Clear any previously defined filter with the  given context.
        """
        for name in self.actions:
            self.clear(name, context=context)

    def clear(self, name: str, context: t.Optional[str] = None) -> None:
        """
        Clear any previously defined action with the given name and context.
        """
        if name not in self.actions:
            return
        self.actions[name] = [
            action for action in self.actions[name] if not action.is_in_context(context)
        ]


def add(name: str) -> t.Callable[[CallableAction], CallableAction]:
    """
    TODO document me (along with other functions here)
    """

    def inner(action_func: CallableAction) -> CallableAction:
        Actions.instance().add(name, action_func)
        return action_func

    return inner


do = Actions.instance().do
clear_all = Actions.instance().clear_all
clear = Actions.instance().clear
