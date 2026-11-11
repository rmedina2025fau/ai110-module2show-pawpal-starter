# PawPal+ Project Reflection

## 1. System Design

Core user actions:

1. Add a pet (name, species, age) to the owner's profile.
2. Schedule a care task for a pet (walk, feeding, meds, appointment) with a time, duration, priority and frequency.
3. See today's schedule across all pets, in time order.

**a. Initial design**

Four classes. UML in `diagrams/uml.mmd`.

- `Task` (dataclass): one activity. Holds description, time (HH:MM), duration, priority, frequency, due date and completion status. Can mark itself complete.
- `Pet` (dataclass): pet details plus its own list of tasks. Adds tasks and reports how many it has.
- `Owner`: holds the pets. Finds a pet by name and returns every task across all pets.
- `Scheduler`: the "brain". Gets tasks from the Owner, picks the ones due on a given day, orders them and formats the output.

Owner has many Pets. Pet has many Tasks. Scheduler only talks to Owner, never to Pets directly.

**b. Design changes**

Added `pet_name` to `Task`. The Scheduler works on one flat list of tasks pulled from all pets, so without it the printed schedule could not say which pet a task belongs to. Keeping it on the task was simpler than returning (pet, task) pairs everywhere.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at three things: the owner's available minutes for the day, task priority, and start time. Priority matters most. Meds and feeding can't be skipped, a brushing session can. Time available comes second because a busy owner can't do everything. Start time only decides the order the plan is shown in.

**b. Tradeoffs**

The plan is greedy. It takes tasks from high to low priority and adds each one if it still fits. If a medium task is too long for the time left, it gets skipped and a shorter low task can still get in. In the demo, a 30 min evening walk is skipped and a 15 min brushing stays. It doesn't find the best possible mix, but it is simple, fast, and easy to explain to the owner, and with a handful of pet tasks a day that is enough.

Conflicts are only warnings. The scheduler does not move tasks around. The owner knows better than the app whether a walk and a feeding can overlap.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code as the agent for Phases 3 to 6. I gave it the phase steps and it wrote the Streamlit wiring, the sorting, filtering, recurring and conflict methods, the tests and the README sections. I ran the tests and the CLI demo after each step. The most useful prompts were the ones that named one method and the exact behavior I wanted, like "a daily task marked complete creates the next one with timedelta".

**b. Judgment and verification**

In Phase 2 the schedule was sorted on the raw "HH:MM" string. That works for "07:30" but a time typed as "7:30" sorts after "12:00". I didn't keep it. Sorting and conflict checks now convert the time to minutes first (`to_minutes`), and I added a test with "7:30" and "12:00" to prove it.

---

## 4. Testing and Verification

**a. What you tested**

12 tests: completing a task, adding tasks to a pet, sorting by time (including "7:30" with no leading zero), daily and weekly recurrence, one-time tasks not repeating, overlap detection, back-to-back tasks, filtering by pet and status, the plan skipping a task when time runs out, and a pet with no tasks. These are the rules the owner actually relies on. If sorting or recurrence breaks, the plan is wrong every day.

**b. Confidence**

4 out of 5. Every scheduling rule has a test and they all pass. Next I would test tasks that run past midnight, two tasks with the exact same time and priority, and an owner with 0 minutes available.

---

## 5. Reflection

**a. What went well**

Keeping the logic in `pawpal_system.py` and the UI in `app.py`. The tests never touch Streamlit, so I could check every rule in under a second.

**b. What you would improve**

Use real `time` objects instead of "HH:MM" strings, let the user edit or delete a task in the UI, and save pets and tasks to a file so they survive closing the app.

**c. Key takeaway**

Design the classes first and the AI output gets much better. With the UML in place, every prompt could point at one class and one method instead of asking for "the scheduler".
