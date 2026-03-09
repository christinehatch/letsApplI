from pathlib import Path

from tools.kanban_cli import _add_task, _move_task


def _seed_board(path: Path) -> None:
    path.write_text(
        (
            "# Test Board\n\n"
            "## Current Work\n\n"
            "- Task A\n\n"
            "## Completed Foundations\n\n"
            "- Done 1\n"
        ),
        encoding="utf-8",
    )


def test_add_and_move_task_keeps_markdown_sections(tmp_path: Path):
    board = tmp_path / "KANBAN.md"
    _seed_board(board)

    _add_task(board, "Implement AI filter", "Current Work")
    _move_task(board, "Task A", "Completed Foundations")

    content = board.read_text(encoding="utf-8")

    assert "## Current Work" in content
    assert "## Completed Foundations" in content

    assert "- Implement AI filter" in content
    assert "- Task A" in content

    # Task A moved out of Current Work section body.
    current_block = content.split("## Current Work", 1)[1].split("## Completed Foundations", 1)[0]
    assert "- Task A" not in current_block
