from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BOARD_PATH = Path("docs/KANBAN.md")


@dataclass
class Section:
    name: str
    header_line: str
    body_lines: list[str]


def _parse_board(path: Path) -> tuple[list[str], list[Section]]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    preamble: list[str] = []
    sections: list[Section] = []

    current: Section | None = None
    saw_section = False

    for line in lines:
        if line.startswith("## "):
            saw_section = True
            if current is not None:
                sections.append(current)
            current = Section(
                name=line[3:].strip(),
                header_line=line,
                body_lines=[],
            )
            continue

        if not saw_section:
            preamble.append(line)
        else:
            if current is None:
                raise ValueError("Malformed board: section state invalid")
            current.body_lines.append(line)

    if current is not None:
        sections.append(current)

    return preamble, sections


def _write_board(path: Path, preamble: list[str], sections: list[Section]) -> None:
    output: list[str] = []
    output.extend(preamble)
    for section in sections:
        output.append(section.header_line)
        output.extend(section.body_lines)

    path.write_text("".join(output), encoding="utf-8")


def _find_section(sections: list[Section], section_name: str) -> Section:
    for section in sections:
        if section.name == section_name:
            return section
    raise ValueError(f"Section not found: {section_name}")


def _count_section_tasks(section: Section) -> int:
    return sum(1 for line in section.body_lines if line.lstrip().startswith("- "))


def _list_tasks(path: Path) -> None:
    _, sections = _parse_board(path)
    for idx, section in enumerate(sections):
        tasks = [
            line.strip()[2:].strip()
            for line in section.body_lines
            if line.lstrip().startswith("- ")
        ]
        print(f"=== {section.name} ({len(tasks)} tasks) ===")
        if not tasks:
            print("(no tasks)")
        else:
            for task in tasks:
                print(f"- {task}")
        if idx < len(sections) - 1:
            print()


def _add_task(path: Path, task: str, section_name: str) -> None:
    preamble, sections = _parse_board(path)
    section = _find_section(sections, section_name)

    section.body_lines.append(f"- {task}\n")

    _write_board(path, preamble, sections)

    if section.name == "Current Work" and _count_section_tasks(section) > 5:
        print(
            "Warning: Current Work exceeds WIP limit (5 tasks). "
            "Consider moving items to Next Layer."
        )


def _print_next_tasks(path: Path, limit: int = 3) -> None:
    _, sections = _parse_board(path)
    section = _find_section(sections, "Current Work")

    tasks = [
        line.strip()[2:].strip()
        for line in section.body_lines
        if line.lstrip().startswith("- ")
    ]

    print("Next tasks:")
    print()
    for idx, task in enumerate(tasks[:limit], start=1):
        print(f"{idx}. {task}")


def _print_progress(path: Path) -> None:
    _, sections = _parse_board(path)
    names = (
        "Completed Foundations",
        "Current Work",
        "Next Layer",
        "Future System",
    )

    print("Progress Summary")
    print()

    for name in names:
        section = _find_section(sections, name)
        count = _count_section_tasks(section)
        print(f"{name}: {count}")


def _print_today(path: Path) -> None:
    _, sections = _parse_board(path)
    current = _find_section(sections, "Current Work")
    next_tasks = [
        line.strip()[2:].strip()
        for line in current.body_lines
        if line.lstrip().startswith("- ")
    ][:3]

    completed = _count_section_tasks(_find_section(sections, "Completed Foundations"))
    current_count = _count_section_tasks(current)
    next_layer = _count_section_tasks(_find_section(sections, "Next Layer"))

    print("Today's Focus")
    print()
    print("Next Tasks:")
    for idx, task in enumerate(next_tasks, start=1):
        print(f"{idx}. {task}")
    print()
    print("Progress:")
    print(f"Completed Foundations: {completed}")
    print(f"Current Work: {current_count}")
    print(f"Next Layer: {next_layer}")


def _move_task(path: Path, task: str, target_section_name: str) -> None:
    preamble, sections = _parse_board(path)
    target = _find_section(sections, target_section_name)

    removed = False
    task_line = f"- {task}"

    for section in sections:
        new_body: list[str] = []
        for line in section.body_lines:
            if not removed and line.strip() == task_line:
                removed = True
                continue
            new_body.append(line)
        section.body_lines = new_body

    if not removed:
        raise ValueError(f"Task not found: {task}")

    target.body_lines.append(f"- {task}\n")

    _write_board(path, preamble, sections)


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m tools.kanban_cli")
    parser.add_argument(
        "--board",
        default=str(DEFAULT_BOARD_PATH),
        help="Path to board markdown file",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list")
    sp.set_defaults(func=lambda args: _list_tasks(Path(args.board)))

    sp = sub.add_parser("add")
    sp.add_argument("task")
    sp.add_argument("section")
    sp.set_defaults(func=lambda args: _add_task(Path(args.board), args.task, args.section))

    sp = sub.add_parser("move")
    sp.add_argument("task")
    sp.add_argument("section")
    sp.set_defaults(func=lambda args: _move_task(Path(args.board), args.task, args.section))

    sp = sub.add_parser("next")
    sp.set_defaults(func=lambda args: _print_next_tasks(Path(args.board)))

    sp = sub.add_parser("progress")
    sp.set_defaults(func=lambda args: _print_progress(Path(args.board)))

    sp = sub.add_parser("today")
    sp.set_defaults(func=lambda args: _print_today(Path(args.board)))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
