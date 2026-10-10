from unittest.mock import patch

from tasks.list_tools import list_tools_task
from tasks.report_status import report_status_task


def test_list_tools_task():
    tools = list_tools_task()
    assert isinstance(tools, list)
    names = [t["name"] for t in tools]
    assert "setup_project" in names
    assert "review_pr" in names
    assert "report_status" in names


@patch("cli.commands.main")
def test_report_status_task(mock_main):
    # Mock the Celery update_state method
    with patch("tasks.report_status.report_status_task.update_state"):
        result = report_status_task(date="2023-10-10")
        assert "Status report generated." in result
        mock_main.assert_called_once_with(["2023-10-10"])
