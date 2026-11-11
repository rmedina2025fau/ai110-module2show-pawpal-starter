from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", layout="centered")
st.title("PawPal+")
st.caption("Plan your pets' care for the day.")

# The Owner lives in session_state so pets and tasks survive Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Owner -------------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes
        )
    )

# --- Pets --------------------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Give the pet a name.")
        elif owner.get_pet(pet_name.strip()):
            st.error(f"{pet_name.strip()} already exists.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species, int(age)))
            st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.write(", ".join(f"{p.name} ({p.species}, {p.task_count()} tasks)" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# --- Tasks -------------------------------------------------------------------
if owner.pets:
    st.subheader("Tasks")
    with st.form("add_task", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
            description = st.text_input("Task", value="Morning walk")
            task_time = st.time_input("Start time", value=None, step=300)
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            if task_time is None:
                st.error("Pick a start time.")
            elif not description.strip():
                st.error("Describe the task.")
            else:
                owner.get_pet(task_pet).add_task(
                    Task(
                        description.strip(),
                        task_time.strftime("%H:%M"),
                        int(duration),
                        priority=priority,
                        frequency=frequency,
                    )
                )
                st.success(f"Added '{description.strip()}' for {task_pet}.")

    today = scheduler.todays_schedule()

    show_pet = st.selectbox("Show tasks for", ["All pets"] + [p.name for p in owner.pets])
    show_status = st.radio("Status", ["All", "Open", "Done"], horizontal=True)
    visible = scheduler.filter_tasks(
        today,
        pet_name=None if show_pet == "All pets" else show_pet,
        completed={"All": None, "Open": False, "Done": True}[show_status],
    )
    if visible:
        st.table(
            [
                {
                    "Time": t.time,
                    "Pet": t.pet_name,
                    "Task": t.description,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority,
                    "Repeats": t.frequency,
                    "Done": "yes" if t.completed else "",
                }
                for t in visible
            ]
        )
    else:
        st.info("No tasks match.")

    open_tasks = scheduler.filter_tasks(today, completed=False)
    if open_tasks:
        labels = [f"{t.time} {t.pet_name}: {t.description}" for t in open_tasks]
        picked = st.selectbox("Mark a task done", labels)
        if st.button("Mark done"):
            task = open_tasks[labels.index(picked)]
            upcoming = scheduler.complete_task(task)
            if upcoming:
                st.success(f"Done. Next '{task.description}' set for {upcoming.due_date.isoformat()}.")
            else:
                st.success("Done.")
            st.rerun()

    # --- Schedule ----------------------------------------------------------------
    st.divider()
    st.subheader(f"Today's plan ({date.today().isoformat()})")

    if st.button("Generate schedule", type="primary"):
        planned, skipped = scheduler.build_plan()

        for warning in scheduler.detect_conflicts(planned):
            st.warning(f"Time conflict: {warning}")

        if planned:
            used = sum(t.duration_minutes for t in planned)
            st.success(f"{len(planned)} tasks planned, {used} of {owner.available_minutes} min used.")
            st.table(
                [
                    {
                        "Time": t.time,
                        "Pet": t.pet_name,
                        "Task": t.description,
                        "Why": scheduler.explain(t),
                    }
                    for t in planned
                ]
            )
        else:
            st.info("Nothing to plan for today.")

        for task, reason in skipped:
            st.info(f"Skipped {task.pet_name} '{task.description}': {reason}.")
