# Mood Mirror 🌤️

Mood Mirror is a beginner-friendly Streamlit wellness journal. Users can record a daily mood check-in, receive simple rule-based self-care suggestions, review recent patterns, and export/import their own data.

# What this project demonstrates

- Python functions, lists, dictionaries, loops, and conditionals
- Streamlit forms, tabs, metrics, charts, and session state
- Pandas DataFrame operations
- Rule-based recommendation logic
- Simple trend/pattern analysis
- CSV import/export
- Privacy-conscious product design

# Important design choice

Mood Mirror is **not a diagnostic tool**. It never tells users that they have a mental-health condition. It only points out patterns in the user's own check-ins and suggests considering professional support when repeated low mood, high stress, or poor sleep appears.

This version does not permanently store private mood data on a public server. Users can download their data as CSV and upload it again later.

# Run locally

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the app:

```powershell
streamlit run app.py
```

Then open the Local URL shown in the terminal.

## Test the dashboard

You can either:
1. Add several check-ins manually using different dates, or
2. Upload `sample_moodmirror_data.csv` from the **My Data** tab.

# Suggested future versions

- Better custom styling
- Weekly/monthly filters
- More pattern comparisons
- Optional local SQLite storage
- Authentication + private database only after learning secure user-data handling
