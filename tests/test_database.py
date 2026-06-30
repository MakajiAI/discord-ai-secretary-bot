from discord_ai_secretary.database import TaskDatabase


def test_add_and_list_open_tasks(tmp_path) -> None:
    db = TaskDatabase(str(tmp_path / "bot.db"))
    db.initialize()

    ids = db.add_tasks(
        "guild-1",
        "channel-1",
        [{"title": "READMEを作成する", "assignee": "まかじ", "due_date": None}],
    )

    tasks = db.list_open_tasks("guild-1")
    assert len(ids) == 1
    assert len(tasks) == 1
    assert tasks[0].title == "READMEを作成する"
    assert tasks[0].assignee == "まかじ"


def test_mark_done(tmp_path) -> None:
    db = TaskDatabase(str(tmp_path / "bot.db"))
    db.initialize()
    task_id = db.add_tasks(
        "guild-1",
        "channel-1",
        [{"title": "タスクを完了する", "assignee": None, "due_date": None}],
    )[0]

    assert db.mark_done("guild-1", task_id) is True
    assert db.list_open_tasks("guild-1") == []
    assert db.mark_done("guild-2", task_id) is False
