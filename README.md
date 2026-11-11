# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Output of `python main.py` (owner has 60 min available):

```
Today's Schedule (2026-11-11) for Renzo
----------------------------------------------------
[ ] 07:30  Rocky    Morning walk        30 min  (high)
[ ] 07:45  Luna     Feeding             10 min  (high)
[ ] 12:00  Luna     Flea medication      5 min  (high)
[ ] 18:00  Rocky    Evening walk        30 min  (medium)
[ ] 20:00  Luna     Brushing            15 min  (low)

Plan for 60 min available
----------------------------------------------------
[ ] 07:30  Rocky    Morning walk        30 min  (high)
[ ] 07:45  Luna     Feeding             10 min  (high)
[ ] 12:00  Luna     Flea medication      5 min  (high)
[ ] 20:00  Luna     Brushing            15 min  (low)
Skipped: Rocky Evening walk (needs 30 min, only 15 left)

Conflicts
----------------------------------------------------
WARNING: Rocky 'Morning walk' (07:30) overlaps Luna 'Feeding' (07:45)

Luna's tasks only
----------------------------------------------------
[ ] 07:45  Luna     Feeding             10 min  (high)
[ ] 12:00  Luna     Flea medication      5 min  (high)
[ ] 20:00  Luna     Brushing            15 min  (low)

Completed 'Feeding'. Next one added for 2026-11-12.
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The suite covers:

- Completing a task flips its status.
- Adding a task to a pet raises its count and tags the pet name.
- Sorting returns tasks in time order even when added out of order, including "7:30" with no leading zero.
- A daily task creates a new task for the next day when completed. A weekly one moves 7 days. A one-time task does not repeat.
- Overlapping tasks are flagged as a conflict. Back-to-back tasks are not.
- Filtering by pet name and by done/open status.
- The plan keeps high priority tasks and skips a low priority one when time runs out.
- A pet with no tasks gives an empty schedule.

Sample test output:

```
tests/test_pawpal.py::test_mark_complete_changes_status PASSED
tests/test_pawpal.py::test_add_task_increases_count PASSED
tests/test_pawpal.py::test_sort_by_time_orders_chronologically PASSED
tests/test_pawpal.py::test_daily_task_creates_next_day_when_completed PASSED
tests/test_pawpal.py::test_weekly_task_moves_seven_days PASSED
tests/test_pawpal.py::test_one_time_task_does_not_repeat PASSED
tests/test_pawpal.py::test_detect_conflicts_flags_overlap PASSED
tests/test_pawpal.py::test_back_to_back_tasks_are_not_a_conflict PASSED
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED
tests/test_pawpal.py::test_build_plan_skips_low_priority_when_time_runs_out PASSED
tests/test_pawpal.py::test_pet_with_no_tasks_gives_empty_schedule PASSED
tests/test_pawpal.py::test_sort_handles_times_without_leading_zero PASSED
12 passed
```

Confidence: 4/5. The core rules are tested. Times are plain "HH:MM" strings, so a task that runs past midnight is not handled.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time` | Converts "HH:MM" to minutes and sorts on that. |
| Filtering | `Scheduler.filter_tasks`, `Scheduler.build_plan` | Filter by pet or done/open. The plan takes tasks by priority and skips any that do not fit in the owner's available minutes, with a reason. |
| Conflict handling | `Scheduler.detect_conflicts` | Compares start and end times. Overlaps return a warning instead of crashing or moving tasks. |
| Recurring tasks | `Task.next_occurrence`, `Scheduler.complete_task` | Completing a daily or weekly task adds the next one using `timedelta` (+1 or +7 days). |

## 📸 Demo Walkthrough

Run it with `streamlit run app.py`.

1. Set the owner name and how many minutes are available today.
2. Add a pet with name, species and age. Duplicate or empty names show an error.
3. Add tasks for a pet: description, start time, duration, priority and how often it repeats.
4. The task table shows today's tasks in time order. Filter it by pet or by open/done.
5. Pick a task and click "Mark done". If it repeats, the next one is added for tomorrow or next week.
6. Click "Generate schedule". The plan lists the chosen tasks with why each one is there, warns about time conflicts, and says which tasks were skipped because time ran out.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
