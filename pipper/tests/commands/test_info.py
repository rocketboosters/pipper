from unittest.mock import MagicMock
from unittest.mock import patch

from pipper import command
from pipper.tests import utils
import lobotomy


@lobotomy.Patch()
def test_info(lobotomized: lobotomy.Lobotomy):
    """Should execut info command without error."""
    lobotomized.add_call("s3", "list_objects_v2", {"contents": []})
    command.run(["info", "fake-package", "--bucket=foo"])


@patch("pipper.s3.list_objects")
@utils.PatchSession()
def test_info_local(boto_mocks: utils.BotoMocks, list_objects: MagicMock):
    """..."""
    list_objects.return_value = utils.make_list_objects_response(contents=[])
    command.run(["info", "fake-package", "--local"])
