from datetime import date
from pathlib import Path

import pytest

from scheduler import (
    DEFAULT_SHIFT_TYPES,
    Employee,
    ScheduleError,
    generate_schedule,
    load_employees_from_csv,
    write_schedule_svg,
)


def test_load_employees_from_csv():
    employees = load_employees_from_csv(Path("data/employees.csv"))
    assert len(employees) == 5
    assert employees[0].full_name == "Jordan Lee"


def test_generate_schedule_creates_expected_count():
    employees = [
        Employee("A", "One", "555", "planner"),
        Employee("B", "Two", "556", "analyst"),
        Employee("C", "Three", "557", "operator"),
    ]
    assignments = generate_schedule(employees, DEFAULT_SHIFT_TYPES, date(2026, 1, 1), day_count=14, seed=7)
    assert len(assignments) == 14 * len(DEFAULT_SHIFT_TYPES)
    assert assignments[0]["date"] == date(2026, 1, 1)


def test_invalid_specialty_raises(tmp_path: Path):
    file = tmp_path / "bad.csv"
    file.write_text(
        "first_name,last_name,phone_number,specialty\nJohn,Doe,123,writer\n",
        encoding="utf-8",
    )

    with pytest.raises(ScheduleError):
        load_employees_from_csv(file)


def test_write_schedule_svg(tmp_path: Path):
    employees = [Employee("A", "One", "555", "engineer")]
    assignments = generate_schedule(employees, DEFAULT_SHIFT_TYPES[:1], date(2026, 1, 1), day_count=1, seed=1)
    output = tmp_path / "schedule.svg"

    write_schedule_svg(assignments, output)

    content = output.read_text(encoding="utf-8")
    assert "<svg" in content
    assert "A One" in content
