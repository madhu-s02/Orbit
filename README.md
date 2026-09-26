# ORBIT

ORBIT is a Python and Streamlit app that turns screen-time data into a black hole and a habit streak into a constellation. Log your daily screen time and habit progress, then explore the visualizations by week, month, or all time.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

On macOS or Linux, activate it with `source venv/bin/activate` instead.

Install the dependencies and start the app:

```shell
pip install streamlit pandas numpy matplotlib pillow
streamlit run app.py
```

`data_log.csv` and `config.json` are created automatically on the first run. Both files are gitignored because they contain your personal data and settings.