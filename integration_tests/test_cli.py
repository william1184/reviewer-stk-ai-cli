import os
import shutil
import subprocess
import sys
import unittest
from unittest import TestCase

current_file = __file__
parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(current_file)))
os.chdir(parent_directory)


def run_command(command, check=True):
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode


class TestCLIFunctional(TestCase):
    _active_command = ''

    def setUp(self):
        # Build the project
        print("Building the project...")
        if run_command("poetry build"):
            print("Build failed", file=sys.stderr)
            sys.exit(1)

        # Create a virtual environment
        print("Creating a virtual environment...")
        if run_command("python -m venv venv"):
            print("Failed to create virtual environment", file=sys.stderr)
            self.fail()

        # Activate the virtual environment
        if os.name == "nt":  # Windows
            activate_script = os.path.join(
                parent_directory, "venv", "Scripts", "activate.bat"
            )
            self._active_command = f"{activate_script}"
        else:  # Unix-like
            activate_script = os.path.join(parent_directory, "venv", "bin", "activate")
            self._active_command = f"source {activate_script}"

            # Install the built package
        print("Installing the package...")
        dist_dir = os.path.join(parent_directory, "..\\", "dist")
        wheel_file = [f for f in os.listdir(dist_dir) if f.endswith(".whl")][0]
        if run_command(
                f"{self._active_command} && pip install  {os.path.join(dist_dir, wheel_file)} --force-reinstall"):
            print("Failed to install the package", file=sys.stderr)
            sys.exit(1)

        print("Removing directory dist...")
        shutil.rmtree(dist_dir)
        print("Removed directory dist...")

    def test_cli_version(self):
        result = subprocess.run(
            [f"{self._active_command}", "&&", "python", "-m", "reviewer_stk_ai", "--version"],
            capture_output=True,
            text=True,
        )

        self.assertIn('reviewer_stk_ai, version 1.0.0', result.stdout)


if __name__ == "__main__":
    unittest.main()
