import os
import tempfile
import unittest

from tutor.commands.context import BaseJobContext
from tutor.jobs import BaseJobRunner
from tutor.plugins import actions, filters
from tutor.types import Config


class TestJobRunner(BaseJobRunner):
    """
    Mock job runner for unit testing.

    This runner does nothing except print the service name and command,
    separated by dashes.
    """

    def run_job(self, service: str, command: str) -> int:
        print(os.linesep.join([f"Service: {service}", "-----", command, "----- "]))
        return 0


def temporary_root() -> "tempfile.TemporaryDirectory[str]":
    """
    Context manager to handle temporary test root.

    This function can be used as follows:

        with temporary_root() as root:
            config = tutor_config.load_full(root)
            ...
    """
    return tempfile.TemporaryDirectory(prefix="tutor-test-root-")


class TestContext(BaseJobContext):
    """
    Click context that will use only test job runners.
    """

    def job_runner(self, config: Config) -> TestJobRunner:
        return TestJobRunner(self.root, config)


class PluginsTestCase(unittest.TestCase):
    """
    TODO document me
    """

    def setUp(self) -> None:
        # TODO this is actually pretty ugly. How do we make sure that plugin
        # filters & actions are cleared after every test?
        filters.clear_filter("apps:tasks")
        filters.clear_filter("env:patches")
        filters.clear_filter("config:base")
        filters.clear_filter("config:defaults")
        filters.clear_filter("plugins:installed")
        filters.clear_filter("plugins:enabled")
        actions.clear_action("plugins:enable")
        super().setUp()
