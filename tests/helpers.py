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
        # Clear plugins actions and filters
        filters.clear_all(context="plugins")
        actions.clear_all(context="plugins")
        super().setUp()
