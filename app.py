from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon=":material/pets:", layout="centered")

PRIORITY_BADGE = {"high": ":red-badge[high]", "medium": ":orange-badge[medium]", "low": ":gray-badge[low]"}

# The Owner lives in session_state so pets and tasks survive Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def load_demo() -> None:
    """Fill the app with two pets and a few tasks so it can be tried right away."""
    rocky = Pet("Rocky", "dog", 4)
    luna = Pet("Luna", "cat", 2)
    owner.add_pet(rocky)
    owner.add_pet(luna)
    rocky.add_task(Task("Morning walk", "07:30", 30, priority="high", frequency="daily"))
    luna.add_task(Task("Feeding", "07:45", 10, priority="high", frequency="daily"))
    luna.add_task(Task("Flea medication", "12:00", 5, priority="high", frequency="weekly"))
    rocky.add_task(Task("Evening walk", "18:00", 30, priority="medium", frequency="daily"))
    luna.add_task(Task("Brushing", "20:00", 15, priority="low"))


def mark_done(task: Task) -> None:
    upcoming = scheduler.complete_task(task)
    if upcoming:
        st.toast(f"Done. Next '{task.description}' set for {upcoming.due_date:%b %d}.", icon=":material/event_repeat:")
    else:
        st.toast(f"'{task.description}' done.", icon=":material/check_circle:")


# --- Header and summary -------------------------------------------------------
st.title("PawPal+")
st.caption(f"Daily care plan for {owner.name} · {date.today():%A, %B %d}")

today = scheduler.todays_schedule()
planned, skipped = scheduler.build_plan()
used = sum(t.duration_minutes for t in planned)

with st.container(horizontal=True):
    st.metric("Pets", len(owner.pets), border=True)
    st.metric("Tasks today", len(today), border=True)
    st.metric("Done", sum(t.completed for t in today), border=True)
    st.metric("Free minutes", owner.available_minutes - used, border=True)

if not owner.pets:
    with st.container(border=True):
        st.markdown("**No pets yet.** Add one in the *Pets* tab, or load sample data to try the app.")
        st.button("Load demo data", icon=":material/auto_awesome:", on_click=load_demo)

plan_tab, tasks_tab, pets_tab = st.tabs(
    [":material/event_note: Today's plan", ":material/checklist: Tasks", ":material/pets: Pets"]
)

# --- Today's plan -------------------------------------------------------------
with plan_tab:
    if owner.available_minutes:
        st.progress(
            min(used / owner.available_minutes, 1.0),
            text=f"{used} of {owner.available_minutes} min planned",
        )

    for warning in scheduler.detect_conflicts(planned):
        st.warning(warning, icon=":material/schedule:")

    if planned:
        with st.container(border=True, gap="small"):
            for task in planned:
                with st.container(horizontal=True, vertical_alignment="center"):
                    st.markdown(
                        f"**{task.time}** &nbsp; {task.description} · {task.pet_name} "
                        f"&nbsp; {PRIORITY_BADGE.get(task.priority, task.priority)}  \n"
                        f":gray[{task.duration_minutes} min · {task.frequency}]"
                    )
                    st.button(
                        "Done",
                        key=f"done_{id(task)}",
                        icon=":material/check:",
                        on_click=mark_done,
                        args=(task,),
                    )
    elif owner.pets:
        st.caption("Nothing left to do today. Add tasks in the *Tasks* tab.")

    if skipped:
        with st.expander(f"Skipped, not enough time ({len(skipped)})", icon=":material/hourglass_empty:"):
            for task, reason in skipped:
                st.markdown(f"{task.time} {task.description} · {task.pet_name} :gray[({reason})]")

    done_today = scheduler.filter_tasks(today, completed=True)
    if done_today:
        with st.expander(f"Done today ({len(done_today)})", icon=":material/task_alt:"):
            for task in done_today:
                st.markdown(f":gray[~~{task.time} {task.description} · {task.pet_name}~~]")

# --- Tasks --------------------------------------------------------------------
with tasks_tab:
    if not owner.pets:
        st.caption("Add a pet first.")
    else:
        with st.form("add_task", clear_on_submit=True):
            st.markdown("**New task**")
            col1, col2 = st.columns(2)
            with col1:
                task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
                description = st.text_input("Task", placeholder="Morning walk")
                task_time = st.time_input("Start time", value=None, step=300)
            with col2:
                duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
                priority = st.segmented_control("Priority", ["high", "medium", "low"], default="medium")
                frequency = st.segmented_control("Repeats", ["once", "daily", "weekly"], default="once")
            if st.form_submit_button("Add task", icon=":material/add:", type="primary"):
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
                            priority=priority or "medium",
                            frequency=frequency or "once",
                        )
                    )
                    st.toast(f"Added '{description.strip()}' for {task_pet}.", icon=":material/check:")
                    st.rerun()

        with st.container(horizontal=True, vertical_alignment="bottom"):
            show_pet = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets], key="filter_pet")
            show_status = st.segmented_control("Status", ["Open", "Done"], key="filter_status")

        visible = scheduler.filter_tasks(
            today,
            pet_name=None if show_pet == "All pets" else show_pet,
            completed={"Open": False, "Done": True}.get(show_status),
        )
        if visible:
            st.dataframe(
                [
                    {
                        "Time": t.time,
                        "Pet": t.pet_name,
                        "Task": t.description,
                        "Minutes": t.duration_minutes,
                        "Priority": t.priority,
                        "Repeats": t.frequency,
                        "Done": t.completed,
                    }
                    for t in visible
                ],
                hide_index=True,
                column_config={"Done": st.column_config.CheckboxColumn()},
            )
        else:
            st.caption("No tasks match.")

# --- Pets and owner -----------------------------------------------------------
with pets_tab:
    col1, col2 = st.columns(2)
    with col1:
        owner.name = st.text_input("Owner name", value=owner.name)
    with col2:
        owner.available_minutes = int(
            st.number_input("Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes, step=15)
        )

    with st.form("add_pet", clear_on_submit=True):
        st.markdown("**New pet**")
        with st.container(horizontal=True, vertical_alignment="bottom"):
            pet_name = st.text_input("Name", placeholder="Rocky")
            species = st.selectbox("Species", ["dog", "cat", "other"])
            age = st.number_input("Age", min_value=0, max_value=40, value=1)
        if st.form_submit_button("Add pet", icon=":material/add:", type="primary"):
            name = pet_name.strip()
            if not name:
                st.error("Give the pet a name.")
            elif owner.get_pet(name):
                st.error(f"{name} already exists.")
            else:
                owner.add_pet(Pet(name, species, int(age)))
                st.toast(f"Added {name}.", icon=":material/pets:")
                st.rerun()

    for pet in owner.pets:
        with st.container(border=True, horizontal=True, vertical_alignment="center"):
            st.markdown(f"**{pet.name}** :gray[{pet.species}, {pet.age} yr]")
            st.badge(f"{pet.task_count()} tasks", color="blue")
