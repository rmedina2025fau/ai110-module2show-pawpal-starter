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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
