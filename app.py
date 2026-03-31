import streamlit as st
from datetime import datetime, timedelta, date

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Ensure an Owner object persists in session_state so it is not recreated on every rerun.
if "owner_obj" not in st.session_state:
    username = owner_name.strip().lower().replace(" ", "_") or "owner"
    st.session_state.owner_obj = Owner(name=owner_name, username=username)
else:
    # Keep the owner display name in sync with the text input
    st.session_state.owner_obj.name = owner_name

# Helper to show owner's tasks grouped by pet
def _show_owner_tasks(owner: Owner):
    pets = owner.view_pets()
    if not pets:
        st.info("No pets added yet. Add a pet to get started.")
        return
    for pet in pets:
        tasks = pet.get_tasks()
        st.write(f"### {pet.name} ({pet.species or 'unknown'})")
        if not tasks:
            st.write("- No tasks")
            continue
        for t in sorted(tasks, key=lambda x: x.task_time):
            st.write(f"- {t.task_time.strftime('%Y-%m-%d %H:%M')}: {t.description} (status={t.status})")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# Button to add a pet to the Owner
if st.button("Add pet"):
    owner = st.session_state.owner_obj
    if owner.find_pet(pet_name) is None:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added pet '{pet_name}'")
    else:
        st.info(f"Pet '{pet_name}' already exists")

if st.button("Add task"):
    owner = st.session_state.owner_obj
    # ensure pet exists
    pet = owner.find_pet(pet_name)
    if pet is None:
        pet = Pet(name=pet_name, species=species)
        owner.add_pet(pet)
    # create a Task; schedule it `duration` minutes from now for demo purposes
    t_time = datetime.now() + timedelta(minutes=int(duration))
    task = Task(description=task_title, task_time=t_time)
    pet.add_task(task)
    st.success(f"Added task '{task_title}' to {pet.name} @ {t_time.strftime('%Y-%m-%d %H:%M')}")

_show_owner_tasks(st.session_state.owner_obj)

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    owner = st.session_state.owner_obj
    upcoming = Scheduler.upcoming_tasks(owner, within=timedelta(days=1))
    if not upcoming:
        st.info("No upcoming tasks in the next 24 hours.")
    else:
        st.subheader("Upcoming tasks (24h)")
        for t in upcoming:
            # find which pet this task belongs to for display
            pet_name_for_task = next((p.name for p in owner.pets if t in p.tasks), "(unknown)")
            st.write(f"- {t.task_time.strftime('%Y-%m-%d %H:%M')} — {pet_name_for_task}: {t.description}")
