import typing as t
import unittest

from tutor.plugins import actions, contexts


class PluginActionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.side_effect_int = 0

    def tearDown(self) -> None:
        super().tearDown()
        actions.clear_all(context="tests")

    def run(self, result: t.Any = None) -> t.Any:
        with contexts.enter("tests"):
            return super().run(result=result)

    def test_add(self) -> None:
        @actions.add("test-action")
        def _test_action_1(increment: int) -> None:
            self.side_effect_int += increment

        @actions.add("test-action")
        def _test_action_2(increment: int) -> None:
            self.side_effect_int += increment * 2

        actions.do("test-action", 1)
        self.assertEqual(3, self.side_effect_int)
