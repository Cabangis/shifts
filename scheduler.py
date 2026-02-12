#!/usr/bin/env python3
"""Shift scheduler for a 2-week period with SVG output."""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Sequence

VALID_SPECIALTIES = {"planner", "analyst", "operator", "engineer"}


@dataclass(frozen=True)
class Employee:
    first_name: str
    last_name: str
    phone_number: str
    specialty: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class ShiftType:
    name: str
    start_hour: int
    end_hour: int


DEFAULT_SHIFT_TYPES = (
    ShiftType("Morning", 6, 14),
    ShiftType("Evening", 14, 22),
    ShiftType("Night", 22, 6),
)


class ScheduleError(ValueError):
    """Raised for invalid scheduler inputs."""


def validate_specialty(raw: str) -> str:
    value = raw.strip().lower()
    if value not in VALID_SPECIALTIES:
        valid = ", ".join(sorted(VALID_SPECIALTIES))
        raise ScheduleError(f"Invalid specialty '{raw}'. Valid options: {valid}")
    return value


def load_employees_from_csv(csv_path: Path) -> list[Employee]:
    employees: list[Employee] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"first_name", "last_name", "phone_number", "specialty"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ScheduleError(f"Employee CSV missing required columns: {', '.join(sorted(missing))}")

        for idx, row in enumerate(reader, start=2):
            try:
                first = row["first_name"].strip()
                last = row["last_name"].strip()
                phone = row["phone_number"].strip()
                specialty = validate_specialty(row["specialty"])
            except KeyError as exc:
                raise ScheduleError(f"Row {idx} missing field {exc}") from exc

            if not first or not last or not phone:
                raise ScheduleError(f"Row {idx} has empty required employee values")

            employees.append(Employee(first, last, phone, specialty))

    if not employees:
        raise ScheduleError("Employee CSV is empty")

    return employees


def generate_schedule(
    employees: Sequence[Employee],
    shift_types: Sequence[ShiftType],
    start_day: date,
    day_count: int = 14,
    seed: int | None = None,
) -> list[dict]:
    if not employees:
        raise ScheduleError("At least one employee is required")
    if not shift_types:
        raise ScheduleError("At least one shift type is required")
    if day_count <= 0:
        raise ScheduleError("day_count must be positive")

    rng = random.Random(seed)
    assignments: list[dict] = []

    for day_offset in range(day_count):
        day = start_day + timedelta(days=day_offset)
        shuffled = list(employees)
        rng.shuffle(shuffled)

        for shift_idx, shift in enumerate(shift_types):
            employee = shuffled[shift_idx % len(shuffled)]
            assignments.append(
                {
                    "date": day,
                    "shift_name": shift.name,
                    "time_range": f"{shift.start_hour:02d}:00-{shift.end_hour:02d}:00",
                    "employee": employee,
                }
            )

    return assignments


def _specialty_color(specialty: str) -> str:
    colors = {
        "planner": "#9ec5fe",
        "analyst": "#a7f3d0",
        "operator": "#fde68a",
        "engineer": "#fbcfe8",
    }
    return colors.get(specialty, "#e5e7eb")


def write_schedule_svg(assignments: Iterable[dict], output_path: Path, title: str = "2-Week Shift Schedule") -> None:
    data = list(assignments)
    if not data:
        raise ScheduleError("Cannot render empty schedule")

    row_h = 30
    header_h = 70
    margin = 30
    width = 980
    height = header_h + row_h * (len(data) + 1) + margin

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        "<style>",
        "text { font-family: Arial, sans-serif; fill: #111827; font-size: 12px; }",
        ".title { font-size: 22px; font-weight: bold; }",
        ".header { font-weight: bold; }",
        "</style>",
        f'<text class="title" x="{margin}" y="35">{title}</text>',
        f'<rect x="{margin}" y="{header_h-20}" width="920" height="28" fill="#dbeafe" stroke="#93c5fd"/>',
        f'<text class="header" x="{margin + 10}" y="{header_h}">Date</text>',
        f'<text class="header" x="{margin + 130}" y="{header_h}">Shift</text>',
        f'<text class="header" x="{margin + 250}" y="{header_h}">Time</text>',
        f'<text class="header" x="{margin + 380}" y="{header_h}">Employee</text>',
        f'<text class="header" x="{margin + 620}" y="{header_h}">Phone</text>',
        f'<text class="header" x="{margin + 760}" y="{header_h}">Specialty</text>',
    ]

    y = header_h + 10
    for idx, entry in enumerate(data):
        employee: Employee = entry["employee"]
        fill = _specialty_color(employee.specialty)
        if idx % 2 == 0:
            lines.append(f'<rect x="{margin}" y="{y - 16}" width="920" height="28" fill="#f9fafb"/>')

        lines.append(f'<rect x="{margin + 745}" y="{y - 14}" width="165" height="20" fill="{fill}" rx="4"/>')
        lines.append(f'<text x="{margin + 10}" y="{y}">{entry["date"].isoformat()}</text>')
        lines.append(f'<text x="{margin + 130}" y="{y}">{entry["shift_name"]}</text>')
        lines.append(f'<text x="{margin + 250}" y="{y}">{entry["time_range"]}</text>')
        lines.append(f'<text x="{margin + 380}" y="{y}">{employee.full_name}</text>')
        lines.append(f'<text x="{margin + 620}" y="{y}">{employee.phone_number}</text>')
        lines.append(f'<text x="{margin + 760}" y="{y}">{employee.specialty.title()}</text>')
        y += row_h

    lines.append("</svg>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a random 2-week employee shift schedule")
    parser.add_argument("--employees", required=True, type=Path, help="Path to employee CSV file")
    parser.add_argument("--output", default=Path("schedule.svg"), type=Path, help="Output SVG path")
    parser.add_argument("--start-date", default=date.today().isoformat(), help="Start date YYYY-MM-DD")
    parser.add_argument("--days", default=14, type=int, help="Number of days to schedule")
    parser.add_argument("--seed", default=None, type=int, help="Optional random seed")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    employees = load_employees_from_csv(args.employees)
    start = date.fromisoformat(args.start_date)
    assignments = generate_schedule(
        employees=employees,
        shift_types=DEFAULT_SHIFT_TYPES,
        start_day=start,
        day_count=args.days,
        seed=args.seed,
    )
    write_schedule_svg(assignments, args.output)
    print(f"Wrote schedule for {args.days} days to {args.output}")


if __name__ == "__main__":
    main()
