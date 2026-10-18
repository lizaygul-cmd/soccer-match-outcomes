# Soccer Match Outcomes: xG, Possession, Form, xGC

**Analysis question:** How are expected goals (xG), possession, recent form, and expected goals conceded (xGC) associated with match outcomes?
**Prediction question:** How accurately can those four variables predict a team's *next* match result?

Data: StatsBomb Open Data, Premier League 2015/16 (380 matches, 760 team-match rows). Credit StatsBomb in any write-up.

## Setup
```bash
git clone <your-repo-url>
cd soccer-match-outcomes
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```
The processed CSV is already in `data/processed/`. To rebuild it from the source (takes a few minutes, needs internet): `python src/build_dataset.py`

## Repo layout
- `data/processed/`: the team-match CSV. `data/DATA_DICTIONARY.md` explains every column.
- `notebooks/`: one numbered notebook per meeting.
- `src/`: reusable code (`build_dataset.py`, plus your own `features.py` and `models.py`).
- `docs/MEETING_PLAN.md`: the exact agenda for all five meetings.

## Team rules
1. Work on a branch (`git checkout -b yourname/task`), open a pull request, and have one other person review before merging to `main`.
2. Never edit the raw CSV. All changes happen in code so any result can be reproduced.
3. Restart the kernel and run all cells before you commit a notebook.
