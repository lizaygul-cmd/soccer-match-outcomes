# Data dictionary: `data/processed/pl_2015_16_team_matches.csv`

Source: StatsBomb Open Data, Premier League 2015/16 (380 matches).
Credit StatsBomb as the data source in anything you present or publish.
Structure: **one row per team per match** (760 rows, 38 rows per team). Each match appears twice, once from each team's perspective.

| Column | Meaning |
|---|---|
| match_id | StatsBomb match ID (same on both rows of a match) |
| date | Match date (YYYY-MM-DD) |
| match_week | League matchweek (1 to 38) |
| team | The team this row describes |
| opponent | The opposing team |
| is_home | 1 if `team` was at home, else 0 |
| goals_for / goals_against | Final score from `team`'s perspective |
| xg | Sum of StatsBomb xG over `team`'s shots in this match (includes penalties, excludes own goals) |
| xgc | Expected goals conceded: the opponent's `xg` in the same match |
| possession_pct | `team`'s share of possession, 0 to 100. Computed as the summed duration of events while `team` held possession divided by the summed duration of all events (events with durations outside 0 to 120 s are ignored) |
| result | W, D or L for `team` |
| points | 3, 1 or 0 |

## Not in the file (you build these)
- **Form**: points earned in the team's previous 5 matches, using earlier matches only. Never include the current match.
- Rolling averages of xg, xgc and possession_pct over previous matches only, for the prediction model.

## Known quirks
- `xg`, `xgc` and `possession_pct` describe the completed match. They are fine for the *analysis* question but cannot be used as inputs for *predicting* that same match.
- Match 3754232 has a corrupted event duration in the raw data. `build_dataset.py` filters it out.
