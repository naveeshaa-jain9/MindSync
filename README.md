# MindSync
MindSync is an intelligent calendar based wellbeing companion designed to estimate workload pressure from a user's daily schedule and provide personalised recovery recommendations.
The system integrates with Google calendar using the official Google calendar API and falls back to a static JSON calendar when live calendar data is unavailable.
MindSync uses an interpretable rule based AI approach rather than a black box predictive model. It analyses calendar structure, workload density, recovery opportunities and context switching to estimate workload related stress risk and recommend suitable wellbeing activities at available times.

---

## Features

- Live Google calendar integration
- JSON calendar fallback
- Calendar event validation and preprocessing
- Workload feature extraction
- Rule based stress risk estimation
- Three independently interpretable heuristics
- Combined workload pressure score
- Compound pressure adjustment
- Personalised recovery recommendations
- Intelligent free slot detection
- Non overlapping recommendation scheduling
- Future aware recommendations for live calendars
- Streamlit dashboard
- Explainable model outputs
- Synthetic evaluation scenarios
- Edge case handling

---

## System Overview

MindSync follows the pipeline below:
```text
Google calendar API
        │
        ├───────────────┐
        │               │
        ▼               ▼
live calendar        JSON fallback
        │               │
        └───────┬───────┘
                ▼
        event preprocessing
                ▼
        feature extraction
                ▼
        rule based heuristics
        ┌───────┼────────┐
        ▼       ▼        ▼
   workload   recovery   context
   density    pressure   switching
        └───────┼────────┘
                ▼
        combined risk score
                ▼
     personalised suggestions
                ▼
        free slot scheduling
                ▼
        streamlit dashboard
```

---

## Rule based AI approach
MindSync uses three interpretable heuristic strategies.

### 1. Workload density
This heuristic estimates pressure from the proportion of the analysed workday occupied by cognitively demanding events.

Signals include:
- total workload minutes
- proportion of the workday occupied
- total meeting minutes
- meeting density

### 2. Recovery pressure
This heuristic estimates whether the user's schedule provides sufficient opportunities for cognitive recovery.
Signals include:
- back-to-back workload events
- short free gaps
- explicit recovery events
- total recovery time
- minimum available free gap

### 3. Context Switching
This heuristic estimates cognitive switching demand based on changes between different workload categories.

Example categories include:
- meetings
- focused work
- lectures
- presentations
- interviews

A schedule containing repeated switches between these activity types can produce a higher context switching score.

---

## Combined risk score

The three heuristic outputs are combined using the following prototype weights:

```text
Workload Density     35%
Recovery Pressure    35%
Context Switching    30%
```

The resulting score is classified as:

```text
0–34     Low
35–64    Moderate
65–100   High
```

MindSync can also apply a compound pressure adjustment when multiple complementary indicators simultaneously show high workload pressure. The score is intended as an interpretable calendar-based workload estimate and is not a clinical measure of psychological stress.

---

## Personalised recommendations

MindSync generates wellbeing interventions according to the dominant sources of schedule pressure.
Examples include:

- Preventative recovery break
- Short recovery break
- Decompression break
- Movement break
- Focus reset
- Transition pause
- Extended recovery break

Recommendations include:
- activity
- duration
- priority
- explanation
- suggested calendar time

MindSync prioritises the strongest recommendations and avoids presenting unnecessary overlapping interventions.

---

## Timing optimisation

MindSync detects available free periods inside the configured workday:

```text
09:00 – 17:00
```

For live Google Calendar analysis, past time slots are excluded from recommendation scheduling.
The scheduling system:
- detects unallocated gaps
- verifies that an activity fits inside the gap
- scores candidate slots
- prefers slots following workload
- prevents overlapping recommendations
- avoids placing multiple recovery activities immediately beside one another where possible

---

## Google calendar integration
MindSync uses the Google Calendar API with OAuth 2.0. The application requests read-only calendar access.
The following files are required locally:
```text
credentials.json
token.json
```
These files contain authentication information and must never be committed to GitHub.
They are therefore excluded using `.gitignore`.

---

## JSON fallback
If live Google Calendar access fails or no usable timed events are available for the current day, MindSync automatically loads:

```text
data/sample_calendar.json
```

The fallback ensures the complete MindSync pipeline can still be demonstrated and tested without live API availability.

---

## Project structure

```text
MindSync/
│
├── app.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── sample_calendar.json
│
├── src/
│   ├── __init__.py
│   ├── calendar_api.py
│   ├── data_loader.py
│   ├── features.py
│   ├── recommendations.py
│   ├── scheduler.py
│   └── stress_engine.py
│
└── tests/
    ├── test_stress.py
    └── test_evaluation.py
```

---

## installation
### 1. Clone the repo

```bash
git clone https://github.com/naveeshaa-jain9/MindSync.git
```

Move into the project:

```bash
cd MindSync
```

### 2.Create a VM
On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3.Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Google Calendar SEtup

To use live Google Calendar integration:

1.Create a project in Google Cloud Console.
2.Enable the Google Calendar API.
3.Configure the OAuth consent screen.
4.Create an OAuth client using the Desktop App application type.
5.Download the OAuth credentials JSON file.
6.Rename the downloaded file to `credentials.json`.
7.Place it in the project root.

Example:

```text
MindSync/
├── credentials.json
├── app.py
├── streamlit_app.py
└── ...
```

On the first successful authentication, MindSync creates:

```text
token.json
```
locally.

Both authentication files are excluded from Git.

---

## Running the command-line application

Run:

```bash
python app.py
```

The terminal application displays:
- calendar source
- calendar events
- extracted features
- heuristic scores
- combined risk score
- explanations
- recommendations
- suggested time slots

---

## Running the streamlit dashboard

Start the interface with:

```bash
streamlit run streamlit_app.py
```

then open the local URL shown by Streamlit, typically:

```text
http://localhost:8501
```

The dashboard displays:
- data source
- analysed date
- workload overview
- combined risk score
- individual heuristic scores
- explainable reasoning
- personalised recommendations
- suggested recovery times
- calendar timeline
- technical feature details

---

## evaluation

MindSync includes synthetic scenario based evaluation.

Run:

```bash
python -m tests.test_evaluation
```

The evaluation currently includes:
- Light Day
- Moderate Day
- High Density Day
- Back-to-Back Heavy
- Context Switch Heavy
- Recovery Rich Day
- Single Event Day
- Empty Day

### evaluation results

| Scenario | Combined Risk | Classification |
|---|---:|---|
| Light Day | 16/100 | Low |
| Moderate Day | 26/100 | Low |
| High Density Day | 96/100 | High |
| Back-to-Back Heavy | 49/100 | Moderate |
| Context Switch Heavy | 42/100 | Moderate |
| Recovery Rich Day | 8/100 | Low |
| Single Event Day | 16/100 | Low |
| Empty Day | 0/100 | Low |

The scenarios are designed to isolate different sources of workload pressure and compare how the three heuristic strategies react.

---

## interpretation of evaluation

The evaluation demonstrates that the heuristics respond differently to different calendar patterns.

For example:
- High-density schedules strongly activate the workload density heuristic.
- Consecutive events strongly increase recovery pressure.
- Frequent changes between activity categories increase context-switching pressure.
- Recovery-rich schedules produce substantially lower scores.
- An empty calendar produces zero workload pressure.

This separation allows MindSync to provide more interpretable explanations than a single undifferentiated rule.

---

## limitations

MindSync currently has several limitations:
- heuristic thresholds are prototype design decisions
- the system does not use physiological stress data
- calendar data cannot capture every source of psychological stress
- event-type classification uses lightweight keyword-based rules
- user-specific stress tolerance is not currently modelled
- the evaluation uses manually constructed synthetic scenarios
- recommendations are wellbeing suggestions rather than clinical advice
- the configured analysis window is currently fixed at 09:00–17:00

---

## future improvements

Possible future development includes:
- personalised heuristic thresholds
- user-configurable workday hours
- machine-learning-based stress prediction
- longitudinal user feedback
- adaptive recommendation ranking
- wearable sensor integration
- physiological stress signals
- richer semantic event classification
- larger real-world evaluation datasets
- integration with additional calendar platforms

---

## privacy and ethics

MindSync requests read only Google Calendar access. The application does not modify calendar events. OAuth credentials and tokens remain local and are excluded from the public GitHub repository. MindSync should not be interpreted as a clinical diagnostic tool. Its output represents an estimate of calendar-based workload pressure based on schedule structure.

---

## Technologies used

- Python
- Streamlit
- Google Calendar API
- OAuth 2.0
- Google API Python Client
- JSON
- Git
- GitHub

---

## Author

Naveesha Jain
ECS537U Design and Build Project in Artificial Intelligence  
Queen Mary University of London

