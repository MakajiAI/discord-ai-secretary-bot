import pytest

from discord_ai_secretary.services.task_parser import TaskParseError, parse_tasks_json


def test_parse_tasks_json_success() -> None:
    raw = '{"tasks":[{"title":"READMEを作成する","assignee":"まかじ","due_date":null}]}'

    tasks = parse_tasks_json(raw)

    assert tasks == [
        {
            "title": "READMEを作成する",
            "assignee": "まかじ",
            "due_date": None,
        }
    ]


def test_parse_tasks_json_invalid_json() -> None:
    with pytest.raises(TaskParseError):
        parse_tasks_json("not json")
