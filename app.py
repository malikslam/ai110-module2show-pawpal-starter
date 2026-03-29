import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.markdown("A pet care planning assistant that schedules your pet's daily tasks.")

st.divider()

# --- Owner Setup ---
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_minutes = st.number_input("Available minutes per day", min_value=10, max_value=480, value=120)
preferences = st.text_input("Preferences (optional)", value="prefers morning walks")

if st.button("Save Owner"):
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes_per_day=int(available_minutes),
        preferences=preferences
    )

if "owner" in st.session_state:
    st.success(f"Owner saved: {st.session_state.owner.name} — {st.session_state.owner.available_minutes_per_day} min/day")

st.divider()

# --- Pet Setup ---
st.subheader("Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=3)
health_notes = st.text_input("Health notes (optional)", value="")

if st.button("Save Pet"):
    if "owner" not in st.session_state:
        st.warning("Save an Owner first before adding a Pet.")
    else:
        st.session_state.pet = Pet(
            name=pet_name,
            species=species,
            age=int(age),
            health_notes=health_notes,
            owner=st.session_state.owner
        )
        # Preserve existing tasks if pet is re-saved
        if "tasks" not in st.session_state:
            st.session_state.tasks = []

if "pet" in st.session_state:
    st.success(f"Pet saved: {st.session_state.pet.name} ({st.session_state.pet.species})")

st.divider()

# --- Task Builder ---
st.subheader("Tasks")

with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["high", "medium", "low"])

    col4, col5, col6 = st.columns(3)
    with col4:
        category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
    with col5:
        time_constraint = st.selectbox("Time of day", ["none", "morning", "evening"])
    with col6:
        is_required = st.checkbox("Required?", value=False)

    submitted = st.form_submit_button("Add Task")
    if submitted:
        if "pet" not in st.session_state:
            st.warning("Save a Pet first before adding tasks.")
        else:
            task = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                time_of_day_constraint=None if time_constraint == "none" else time_constraint,
                is_required=is_required,
            )
            st.session_state.pet.tasks.append(task)

if "pet" in st.session_state and st.session_state.pet.tasks:
    st.write(f"**{len(st.session_state.pet.tasks)} task(s) added:**")
    st.table([{
        "title": t.title,
        "duration_minutes": t.duration_minutes,
        "priority": t.priority,
        "category": t.category,
        "time_of_day_constraint": t.time_of_day_constraint,
        "is_required": t.is_required,
    } for t in st.session_state.pet.tasks])
    if st.button("Clear all tasks"):
        st.session_state.pet.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule Generation ---
st.subheader("Generate Schedule")
plan_weekday = st.selectbox("Today is", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

if st.button("Generate schedule", type="primary"):
    if "owner" not in st.session_state:
        st.warning("Save an Owner first.")
    elif "pet" not in st.session_state:
        st.warning("Save a Pet first.")
    elif not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        pet = st.session_state.pet
        scheduler = Scheduler(pet=pet, plan_weekday=plan_weekday)
        plan = scheduler.generate_plan()

        st.success(f"Schedule generated for {pet.name} — {plan.total_time()} min total")

        if plan.scheduled:
            st.markdown("### Scheduled Tasks")
            for s in plan.scheduled:
                badge = "🔴" if s.task.priority == "high" else "🟡" if s.task.priority == "medium" else "🟢"
                st.markdown(f"**{s.start_time}** {badge} {s.task.title} `{s.task.duration_minutes} min`")
                st.caption(s.reason)

        if plan.skipped:
            st.markdown("### Skipped Tasks")
            for t in plan.skipped:
                st.markdown(f"- ~~{t.title}~~ ({t.duration_minutes} min — didn't fit)")
