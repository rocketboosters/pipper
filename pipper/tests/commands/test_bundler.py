import os
import pathlib
import shutil
import tempfile

import pipper
from pipper import command

ROOT_DIRECTORY = pathlib.Path(pipper.__file__).parent.parent.absolute()
SCENARIO_DIRECTORY = ROOT_DIRECTORY.joinpath("testing_scenarios")


def test_bundle():
    """
    Should successfully bundle the hello_pipper project into a pipper
    file in a temporary directory and verify that file exists.
    """
    current_directory = pathlib.Path(os.curdir).absolute()
    directory = tempfile.mkdtemp()
    os.chdir(directory)

    project_directory = SCENARIO_DIRECTORY.joinpath("hello_pipper")
    try:
        command.run(
            [
                "bundle",
                f"--output={str(directory)}",
                str(project_directory),
            ]
        )
        filename = next(
            (x for x in os.listdir(directory) if x.endswith(".pipper")), None
        )
        assert filename
        assert filename.startswith("hello_pipper-v")
    finally:
        os.chdir(str(current_directory))
        shutil.rmtree(directory)


def test_bundle_poetry():
    """
    Should successfully bundle the hello_pipper_poetry project into a pipper
    file in a temporary directory and verify that file exists.
    """
    current_directory = pathlib.Path(os.curdir).absolute()
    directory = tempfile.mkdtemp()
    os.chdir(directory)

    project_directory = SCENARIO_DIRECTORY.joinpath("hello_pipper_poetry")
    try:
        command.run(
            [
                "bundle",
                f"--output={str(directory)}",
                str(project_directory),
            ]
        )
        filename = next(
            (x for x in os.listdir(directory) if x.endswith(".pipper")), None
        )
        assert filename
        assert filename.startswith("hello-pipper-poetry-v")
    finally:
        os.chdir(str(current_directory))
        shutil.rmtree(directory)


def test_bundle_without_pipper_dot_json():
    """
    Should be able to successfully bundle the hello_pipper project into a
    pipper file even if no `pipper.(json|yaml)` file is given.
    """
    current_directory = pathlib.Path(os.curdir).absolute()
    directory = tempfile.mkdtemp()
    os.chdir(directory)
    template_directory = SCENARIO_DIRECTORY.joinpath("hello_pipper")
    shutil.copytree(template_directory, directory, dirs_exist_ok=True)
    os.remove(pathlib.Path(directory).joinpath("pipper.json"))

    try:
        command.run(
            [
                "bundle",
                f"--output={str(directory)}",
                str(directory),
            ]
        )
        filename = next(
            (x for x in os.listdir(directory) if x.endswith(".pipper")), None
        )
        assert filename
        assert filename.startswith("hello_pipper-v")
    finally:
        os.chdir(str(current_directory))
        shutil.rmtree(directory)
