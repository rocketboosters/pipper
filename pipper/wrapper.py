import os
import subprocess
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import distributions
from importlib.metadata import version as get_version

from packaging.version import parse as parse_version

from pipper import versioning
from pipper.environment import Environment


def update_required(env: Environment, package_name: str, install_version: str) -> bool:
    """ """
    existing = status(env, package_name)

    if not existing:
        return True

    version = (
        versioning.deserialize(install_version)
        if install_version.startswith("v")
        else install_version
    )

    current = parse_version(existing.version)
    target = parse_version(version)
    return current != target


def clean_path(path: str) -> str:
    """Returns a fully-qualified absolute path for the source"""
    path = os.path.expanduser(path) if path.startswith("~") else path
    return os.path.realpath(path)


def status(env: Environment, package_name: str):
    """..."""
    if env.target_directory:
        # importlib.metadata.distributions doesn't support path parameter,
        # so we need to temporarily modify sys.path
        import sys

        target_path = str(env.target_directory)
        if target_path not in sys.path:
            sys.path.insert(0, target_path)
            try:
                finder = (p for p in distributions() if p.name == package_name)
                return next(finder, None)
            finally:
                sys.path.remove(target_path)
        else:
            finder = (p for p in distributions() if p.name == package_name)
            return next(finder, None)

    try:
        # Return a simple object with version attribute
        class Distribution:
            def __init__(self, name, ver):
                self.name = name
                self.version = ver
                self.project_name = name

        ver = get_version(package_name)
        return Distribution(package_name, ver)
    except PackageNotFoundError:
        return None
    except Exception:
        raise


def install_wheel(
    wheel_path: str,
    to_user: bool = False,
    target_directory: str | None = None,
    dry_run: bool = False,
    use_pip_legacy_resolver: bool = False,
):
    """
    Installs the specified wheel using the pip associated with the
    executing python.
    """
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        wheel_path,
    ]
    if use_pip_legacy_resolver:
        cmd.append("--use-deprecated=legacy-resolver")

    cmd += ["--user"] if to_user else []
    cmd += [f"--target={clean_path(target_directory)}"] if target_directory else []
    print("[COMMAND]:\n", " ".join(cmd).replace(" --", "\n  --"))

    if dry_run:
        print(f"[DRY_RUN]: Skipped wheel installation of {wheel_path}.")
    else:
        result = subprocess.run(cmd)
        result.check_returncode()


def install_pypi(
    package_name: str,
    to_user: bool = False,
    target_directory: str | None = None,
    dry_run: bool = False,
    use_pip_legacy_resolver: bool = False,
):
    """
    Installs the specified package from pypi using pip.
    """
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        package_name,
    ]
    if use_pip_legacy_resolver:
        cmd.append("--use-deprecated=legacy-resolver")

    cmd += ["--user"] if to_user else []
    cmd += [f"--target={clean_path(target_directory)}"] if target_directory else []
    print("[COMMAND]:\n", " ".join(cmd).replace(" --", "\n  --"))

    if dry_run:
        print(f"[DRY_RUN]: Skipped pypi installation of {package_name}.")
    else:
        result = subprocess.run(cmd)
        result.check_returncode()


def install_conda(
    package: str | dict,
    to_user: bool = False,
    target_directory: str | None = None,
    dry_run: bool = False,
):
    """
    Installs the specified package using conda.
    """
    if isinstance(package, dict):
        name = package["name"]
        channel = package.get("channel")
    else:
        name = package
        channel = None

    cmd = [
        sys.executable,
        "-m",
        "conda",
        "install",
        name,
    ]
    cmd += ["--channel", channel] if channel else []
    cmd += ["--user"] if to_user else []
    cmd += [f"--prefix={clean_path(target_directory)}"] if target_directory else []
    print("[COMMAND]:\n", " ".join(cmd).replace(" --", "\n  --"))

    if dry_run:
        print(f"[DRY_RUN]: Skipped conda installation of {name}.")
    else:
        result = subprocess.run(cmd)
        result.check_returncode()
