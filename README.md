# Shift Scheduler

Simple Python scheduler that:

- Accepts employee first/last name, phone number, and career specialty (`planner`, `analyst`, `operator`, `engineer`).
- Provides shift schedule types (Morning, Evening, Night).
- Randomly assigns employees to shifts.
- Produces a **graphical schedule** (SVG) that shows shift coverage for a 2-week period.

## Input format

Create a CSV file with these columns:

```csv
first_name,last_name,phone_number,specialty
Jordan,Lee,555-0100,planner
Riley,Patel,555-0101,analyst
Sam,Nguyen,555-0102,operator
Taylor,Brown,555-0103,engineer
```

A sample file exists at `data/employees.csv`.

## Run

```bash
python3 scheduler.py --employees data/employees.csv --output schedule.svg --days 14 --seed 42
```

This writes `schedule.svg`, which can be opened in any browser or image viewer.

## Test

```bash
python3 -m pytest -q
```
