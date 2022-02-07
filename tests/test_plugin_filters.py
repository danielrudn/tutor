import typing as t
import unittest

from tutor.plugins import contexts, filters


class PluginFiltersTests(unittest.TestCase):
    def tearDown(self) -> None:
        super().tearDown()
        filters.clear_all(context="tests")

    def run(self, result: t.Any = None) -> t.Any:
        with contexts.enter("tests"):
            return super().run(result=result)

    def test_add(self) -> None:
        @filters.add("tests:count-sheeps")
        def filter1(value: int) -> int:
            return value + 1

        value = filters.apply("tests:count-sheeps", 0)
        self.assertEqual(1, value)

    def test_add_items(self) -> None:
        @filters.add("tests:add-sheeps")
        def filter1(sheeps: t.List[int]) -> t.List[int]:
            return sheeps + [0]

        filters.add_item("tests:add-sheeps", 1)
        filters.add_item("tests:add-sheeps", 2)
        filters.add_items("tests:add-sheeps", [3, 4])

        sheeps: t.List[int] = filters.apply("tests:add-sheeps", [])
        self.assertEqual([0, 1, 2, 3, 4], sheeps)

    def test_filter_class(self) -> None:
        filtre = filters.Filter(lambda _: 1)
        self.assertTrue(filtre.is_in_context(None))
        self.assertFalse(filtre.is_in_context("customcontext"))
        self.assertEqual(1, filtre.apply(0))
        self.assertEqual(0, filtre.apply(0, context="customcontext"))

    def test_filter_context(self) -> None:
        with contexts.enter("testcontext"):
            filters.add_item("test:sheeps", 1)
        filters.add_item("test:sheeps", 2)

        self.assertEqual([1, 2], filters.apply("test:sheeps", []))
        self.assertEqual([1], filters.apply("test:sheeps", [], context="testcontext"))

    def test_clear_context(self) -> None:
        with contexts.enter("testcontext"):
            filters.add_item("test:sheeps", 1)
        filters.add_item("test:sheeps", 2)

        self.assertEqual([1, 2], filters.apply("test:sheeps", []))
        filters.clear("test:sheeps", context="testcontext")
        self.assertEqual([2], filters.apply("test:sheeps", []))
