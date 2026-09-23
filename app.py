import streamlit as st
import pandas as pd
from datetime import date


# PAGE SETUP
st.set_page_config(
    page_title="Mood Mirror",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Mood Mirror")
st.caption("A simple daily mood journal that tracks your emotion pattern everyday.")

st.info(
    "MoodMirror is a wellness tracker tool, not a medical or mental-health diagnosis. "
    "Its suggestions are general self-care ideas. If your mood is persistently low, "
    "your stress feels unmanageable, or your daily life is being affected, consider "
    "talking with a qualified health professional.")



# SESSION STORAGE
    # Keep the user's data only for the current Streamlit session.
    # Avoids storing private mood data on a public server.
if "entries" not in st.session_state:
    st.session_state.entries = []


# HELPER FUNCTIONS
def to_bool(value):
    """Convert CSV values such as True/'True'/1 into real booleans."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def get_dataframe():
    """Turn the session list into a clean pandas DataFrame."""
    if not st.session_state.entries:
        return pd.DataFrame()

    df = pd.DataFrame(st.session_state.entries)

    # Convert columns to the correct types.
    df["date"] = pd.to_datetime(df["date"])
    df["mood"] = pd.to_numeric(df["mood"])
    df["stress"] = pd.to_numeric(df["stress"])
    df["energy"] = pd.to_numeric(df["energy"])
    df["sleep_hours"] = pd.to_numeric(df["sleep_hours"])
    df["outside"] = df["outside"].apply(to_bool)
    df["exercise"] = df["exercise"].apply(to_bool)

    return df.sort_values("date")


def save_or_update_entry(record):
    """
    Save one check-in.
    If the user already has an entry for that date,
    replace it instead of creating a duplicate.
    """
    record_date = record["date"]

    for index, existing in enumerate(st.session_state.entries):
        if existing["date"] == record_date:
            st.session_state.entries[index] = record
            return "updated"

    st.session_state.entries.append(record)
    return "added"


def build_daily_advice(mood, stress, energy, sleep_hours, social, outside, exercise):
    """Create simple, rule-based suggestions for today's check-in."""
    advice = []

    if mood <= 2:
        advice.append(
            "Keep today's goal small. Choose one manageable task instead of trying to fix everything at once."
        )

    if stress >= 4:
        advice.append(
            "Your stress is high today. Try a short reset: step away for 10 minutes, breathe slowly, "
            "and write down the single most important thing you need to handle next."
        )

    if sleep_hours < 6:
        advice.append(
            "You logged less than 6 hours of sleep. If possible, protect some extra wind-down time tonight "
            "and avoid adding unnecessary tasks late in the day."
        )

    if energy <= 2:
        advice.append(
            "Your energy is low. Consider a lighter plan today and check the basics: food, water, rest, and breaks."
        )

    if social == "Not connected":
        advice.append(
            "You felt disconnected today. A small social step can count—text someone you trust, study near a friend, "
            "or spend time in a shared space."
        )

    if not outside:
        advice.append(
            "If it is practical for you, try spending 10–15 minutes outside or taking a short walk."
        )

    if not exercise and energy >= 2:
        advice.append(
            "A little movement may help you reset. It does not need to be a workout—a short walk or stretch is enough."
        )

    if not advice:
        advice.append(
            "Your check-in looks fairly balanced today. Notice what helped and try to repeat one of those habits tomorrow."
        )

    return advice


def build_pattern_insights(df):
    """
    Look at recent check-ins and return:
    - observations: neutral patterns in the data
    - support_messages: non-diagnostic reminders to consider extra support
    """
    observations = []
    support_messages = []

    if df.empty:
        return observations, support_messages

    recent = df.tail(7)
    n = len(recent)

    avg_mood = recent["mood"].mean()
    avg_stress = recent["stress"].mean()
    avg_sleep = recent["sleep_hours"].mean()

    low_mood_count = int((recent["mood"] <= 2).sum())
    high_stress_count = int((recent["stress"] >= 4).sum())
    short_sleep_count = int((recent["sleep_hours"] < 6).sum())

    # General patterns
    if n >= 3:
        common_factor = recent["main_factor"].mode()
        if not common_factor.empty:
            observations.append(
                f"Your most frequently selected mood factor in recent check-ins is **{common_factor.iloc[0]}**."
            )

    if n >= 4:
        outside_yes = recent[recent["outside"]]["mood"]
        outside_no = recent[~recent["outside"]]["mood"]

        if len(outside_yes) >= 2 and len(outside_no) >= 2:
            difference = outside_yes.mean() - outside_no.mean()
            if difference >= 0.5:
                observations.append(
                    "Your mood has tended to be higher on recent days when you spent time outside."
                )
            elif difference <= -0.5:
                observations.append(
                    "In your recent entries, spending time outside has not been associated with a higher mood score."
                )

        exercise_yes = recent[recent["exercise"]]["mood"]
        exercise_no = recent[~recent["exercise"]]["mood"]

        if len(exercise_yes) >= 2 and len(exercise_no) >= 2:
            difference = exercise_yes.mean() - exercise_no.mean()
            if difference >= 0.5:
                observations.append(
                    "Your mood has tended to be higher on recent days when you did some exercise or movement."
                )

    # Non-diagnostic support prompts
    if n >= 5 and low_mood_count >= 4:
        support_messages.append(
            "You have logged a low mood in many of your recent check-ins. This does not diagnose a condition, "
            "but if this pattern continues or is affecting school, work, sleep, relationships, or daily functioning, "
            "consider talking with a counselor, doctor, or other qualified mental-health professional."
        )

    if n >= 5 and high_stress_count >= 4:
        support_messages.append(
            "High stress has appeared frequently in your recent check-ins. If it feels difficult to manage on your own, "
            "consider reaching out to someone you trust or a qualified professional for additional support."
        )

    if n >= 5 and short_sleep_count >= 4:
        support_messages.append(
            "You have logged short sleep on many recent check-ins. Persistent sleep problems can affect mood and energy, "
            "so consider discussing them with a health professional if they continue."
        )

    if n >= 5 and avg_mood <= 2.2 and avg_stress >= 4:
        support_messages.append(
            "Your recent entries show a combination of low mood and high stress. Consider getting extra support rather "
            "than relying only on this app."
        )

    return observations, support_messages


# MAIN APP TABS
checkin_tab, dashboard_tab, data_tab = st.tabs(
    ["📝 Daily Check-In", "📊 Dashboard", "🔐 My Data"]
)


# DAILY CHECK-IN TAB
with checkin_tab:
    st.subheader("How are you feeling today?")

    mood_labels = {
        1: "😣 Very low",
        2: "😔 Low",
        3: "😐 Okay",
        4: "🙂 Good",
        5: "😄 Great",
    }

    with st.form("daily_checkin"):
        checkin_date = st.date_input("Date", value=date.today())

        mood = st.select_slider(
            "Overall mood",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda value: mood_labels[value]
        )

        stress = st.slider(
            "Stress level",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = very low stress, 5 = very high stress"
        )

        energy = st.slider(
            "Energy level",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = very low energy, 5 = very high energy"
        )

        sleep_hours = st.number_input(
            "How many hours did you sleep?",
            min_value=0.0,
            max_value=14.0,
            value=7.0,
            step=0.5
        )

        social = st.selectbox(
            "How socially connected did you feel today?",
            ["Not connected", "A little connected", "Connected"]
        )

        col1, col2 = st.columns(2)

        with col1:
            outside = st.checkbox("I spent some time outside")

        with col2:
            exercise = st.checkbox("I did some exercise or intentional movement")

        main_factor = st.selectbox(
            "What affected your mood the most today?",
            [
                "School",
                "Work",
                "Relationships",
                "Health",
                "Money",
                "Sleep",
                "Family",
                "Social life",
                "Nothing specific",
                "Other",
            ]
        )

        note = st.text_area(
            "Optional note",
            placeholder="Anything you want to remember about today?"
        )

        submitted = st.form_submit_button("Save Check-In", type="primary")

    if submitted:
        record = {
            "date": checkin_date.isoformat(),
            "mood": mood,
            "mood_label": mood_labels[mood],
            "stress": stress,
            "energy": energy,
            "sleep_hours": sleep_hours,
            "social": social,
            "outside": outside,
            "exercise": exercise,
            "main_factor": main_factor,
            "note": note,
        }

        result = save_or_update_entry(record)

        if result == "added":
            st.success("Check-in saved!")
        else:
            st.success("You already had a check-in for this date, so it was updated.")

        st.markdown("#### Suggestions for today")
        advice = build_daily_advice(
            mood=mood,
            stress=stress,
            energy=energy,
            sleep_hours=sleep_hours,
            social=social,
            outside=outside,
            exercise=exercise,
        )

        for suggestion in advice:
            st.write(f"• {suggestion}")


# DASHBOARD TAB
with dashboard_tab:
    st.subheader("Your recent patterns")

    df = get_dataframe()

    if df.empty:
        st.write("You do not have any check-ins yet. Add your first one in the Daily Check-In tab.")
    else:
        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:
            st.metric("Check-ins", len(df))

        with metric2:
            st.metric("Average mood", f"{df['mood'].mean():.1f} / 5")

        with metric3:
            st.metric("Average stress", f"{df['stress'].mean():.1f} / 5")

        with metric4:
            st.metric("Average sleep", f"{df['sleep_hours'].mean():.1f} hrs")

        st.markdown("#### Mood, stress, and energy over time")

        chart_df = df.set_index("date")[["mood", "stress", "energy"]]
        st.line_chart(chart_df)

        st.markdown("#### Most common mood factors")
        factor_counts = df["main_factor"].value_counts()
        st.bar_chart(factor_counts)

        observations, support_messages = build_pattern_insights(df)

        st.markdown("#### Patterns noticed")

        if observations:
            for observation in observations:
                st.write(f"• {observation}")
        else:
            st.write("Add a few more check-ins before MoodMirror starts looking for patterns.")

        if support_messages:
            st.markdown("#### Consider extra support")
            for message in support_messages:
                st.warning(message)

        st.markdown("#### Check-in history")

        display_columns = [
            "date",
            "mood_label",
            "stress",
            "energy",
            "sleep_hours",
            "social",
            "outside",
            "exercise",
            "main_factor",
            "note",
        ]

        display_df = df[display_columns].copy()
        display_df["date"] = display_df["date"].dt.date

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


# MY DATA TAB
with data_tab:
    st.subheader("Keep your data under your control")

    st.write(
        "This version does not use accounts or permanently store personal mood data on the public server. "
        "You can download your check-ins as a CSV file and upload them again later."
    )

    current_df = get_dataframe()

    if not current_df.empty:
        download_df = current_df.copy()
        download_df["date"] = download_df["date"].dt.date.astype(str)

        csv_data = download_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download My Check-Ins",
            data=csv_data,
            file_name="moodmirror_checkins.csv",
            mime="text/csv"
        )

    uploaded_file = st.file_uploader(
        "Upload a previous MoodMirror CSV",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)

            required_columns = {
                "date",
                "mood",
                "mood_label",
                "stress",
                "energy",
                "sleep_hours",
                "social",
                "outside",
                "exercise",
                "main_factor",
                "note",
            }

            if not required_columns.issubset(uploaded_df.columns):
                st.error("This CSV does not look like a MoodMirror export.")
            else:
                # Normalize booleans before storing.
                uploaded_df["outside"] = uploaded_df["outside"].apply(to_bool)
                uploaded_df["exercise"] = uploaded_df["exercise"].apply(to_bool)

                if st.button("Load Uploaded Data"):
                    st.session_state.entries = uploaded_df.to_dict("records")
                    st.success("Your previous check-ins were loaded.")
                    st.rerun()

        except Exception:
            st.error("The CSV could not be read. Make sure it is a valid MoodMirror export.")

    st.divider()

    if st.session_state.entries:
        if st.button("Clear All Session Data"):
            st.session_state.entries = []
            st.rerun()

    st.caption(
        "If you ever feel unsafe or unable to keep yourself safe, use local emergency services or a crisis resource "
        "available in your country. MoodMirror is not designed for emergency support."
    )
