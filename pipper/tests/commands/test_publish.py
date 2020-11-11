from unittest.mock import MagicMock
from unittest.mock import patch
import json

import lobotomy
import pytest

from pipper import command


def test_publish_no_file():
    """Should raise error if no bundle exists."""
    with pytest.raises(FileNotFoundError):
        command.run(["publish", "foo-does-not-exist"])


@lobotomy.Patch()
@patch("pipper.publisher.open")
@patch("os.path.getsize")
@patch("os.path.exists")
@patch("zipfile.ZipFile")
def test_publish(
    zipfile_zipfile: MagicMock,
    os_path_exists: MagicMock,
    os_path_getsize: MagicMock,
    publisher_open: MagicMock,
    lobotomized: lobotomy.Lobotomy,
):
    """Should successfully publish a bundle."""
    lobotomized.add_call("s3", "list_objects", {"Contents": []})
    lobotomized.add_call("s3", "put_object", {})
    os_path_getsize.return_value = 123
    os_path_exists.return_value = True
    zipfile_zipfile.return_value.__enter__.return_value.read.return_value = json.dumps(
        {
            "name": "foo",
            "version": "0.1.123",
            "safe_version": "v0-1-123",
            "timestamp": "2021-01-01T12:23:34Z",
        }
    )

    command.run(["publish", "foo", "--bucket=foo-bucket"])


@lobotomy.Patch()
@patch("pipper.publisher.open")
@patch("os.path.getsize")
@patch("os.path.exists")
@patch("zipfile.ZipFile")
def test_publish_skipped(
    zipfile_zipfile: MagicMock,
    os_path_exists: MagicMock,
    os_path_getsize: MagicMock,
    publisher_open: MagicMock,
    lobotomized: lobotomy.Lobotomy,
):
    """Should skip publishing if the target bundle version is already published."""
    lobotomized.add_call("s3", "list_objects", {"Contents": [{}]})
    os_path_exists.return_value = True
    zipfile_zipfile.return_value.__enter__.return_value.read.return_value = json.dumps(
        {
            "name": "foo",
            "version": "0.1.123",
            "safe_version": "v0-1-123",
            "timestamp": "2021-01-01T12:23:34Z",
        }
    )

    command.run(["publish", "foo", "--bucket=foo-bucket"])
    os_path_getsize.assert_not_called()
