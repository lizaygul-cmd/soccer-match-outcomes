"""
Build a team-match table from StatsBomb Open Data.

Default: Premier League 2015/16 (competition_id=2, season_id=27), the full
380-match season. Output: one row per team per match (760 rows).

Usage:
    python src/build_dataset.py
    python src/build_dataset.py --competition 2 --season 27 --out data/processed/pl_2015_16_team_matches.csv

Data: StatsBomb Open Data (https://github.com/statsbomb/open-data).
If you publish or present results, credit StatsBomb as the data source.
"""
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"


def get_json(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def match_team_stats(match_id):
    """Return (xg_by_team, possession_seconds_by_team) for one match."""
    events = get_json(f"{BASE}/events/{match_id}.json")
    xg, poss = {}, {}
    for e in events:
        team = e["team"]["name"]
        if e["type"]["name"] == "Shot":
            xg[team] = xg.get(team, 0.0) + e["shot"].get("statsbomb_xg", 0.0)
        pt = e.get("possession_team", {}).get("name")
        dur = e.get("duration")
        # Ignore missing and impossible durations (the source data has at least
        # one event with a negative duration of about -2,660 s).
        if pt and dur is not None and 0 <= dur <= 120:
            poss[pt] = poss.get(pt, 0.0) + dur
    return xg, poss


def main(competition, season, out):
    matches = get_json(f"{BASE}/matches/{competition}/{season}.json")
    matches = [m for m in matches if m["match_status"] == "available"]
    print(f"{len(matches)} matches found")

    ids = [m["match_id"] for m in matches]
    with ThreadPoolExecutor(max_workers=8) as ex:
        stats = list(ex.map(match_team_stats, ids))

    rows = []
    for m, (xg, poss) in zip(matches, stats):
        home = m["home_team"]["home_team_name"]
        away = m["away_team"]["away_team_name"]
        hs, as_ = m["home_score"], m["away_score"]
        total_poss = sum(poss.values()) or 1.0
        for team, opp, is_home, gf, ga in [
            (home, away, 1, hs, as_),
            (away, home, 0, as_, hs),
        ]:
            result = "W" if gf > ga else ("D" if gf == ga else "L")
            rows.append(
                {
                    "match_id": m["match_id"],
                    "date": m["match_date"],
                    "match_week": m["match_week"],
                    "team": team,
                    "opponent": opp,
                    "is_home": is_home,
                    "goals_for": gf,
                    "goals_against": ga,
                    "xg": round(xg.get(team, 0.0), 3),
                    "xgc": round(xg.get(opp, 0.0), 3),
                    "possession_pct": round(100 * poss.get(team, 0.0) / total_poss, 2),
                    "result": result,
                    "points": 3 if result == "W" else (1 if result == "D" else 0),
                }
            )

    df = pd.DataFrame(rows).sort_values(
        ["date", "match_id", "is_home"], ascending=[True, True, False]
    )
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--competition", type=int, default=2)
    ap.add_argument("--season", type=int, default=27)
    ap.add_argument("--out", default="data/processed/pl_2015_16_team_matches.csv")
    a = ap.parse_args()
    main(a.competition, a.season, a.out)
