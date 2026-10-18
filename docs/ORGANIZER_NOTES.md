# Organizer notes (do not share before the relevant meeting)

Verified on the prebuilt dataset:
- 660 team-match rows have a 5-match Form (760 minus 5 matches for each of 20 teams). That is 330 usable matches (matchweeks 6 to 38). Chronological split: first 220 train, last 110 test.
- Home result split among the 330 usable matches: about 43% home win, 28% draw, 29% away win.
- Same-match averages: winners average about 1.64 xG and 0.97 xGC; losers average about 0.97 xG and 1.64 xGC. Mean possession is almost identical for winners, drawers and losers (about 50%). Do not tell the team this in advance; it is a genuine finding.
- Correlations among the four difference features: form vs xg 0.50, form vs xgc -0.48, xgc vs possession -0.45. Expect some collinearity.

**Set expectations for Meeting 4.** A quick prototype with this exact setup (multinomial logistic regression on the four differences) gave test accuracy of about 46% against a 44.5% always-predict-the-majority baseline, and log loss of about 1.04 against 1.08 for the baseline. That is a small improvement, and with only 110 test matches the drop-one differences are within noise. A modest result is a legitimate finding; the point is a clean, leakage-free method.

Reference for the Form calculation (give only if a pair is stuck):
```python
df = df.sort_values(["team", "date"])
df["form"] = df.groupby("team")["points"].transform(lambda s: s.shift(1).rolling(5).sum())
```
Pitfalls to watch: forgetting `shift(1)` leaks the current match; sorting by match_id instead of date can reorder matches; computing form after a random split.

Possible extensions if the team finishes early: add a second season or league for more matches, an elo-style team strength rating, home advantage as a feature, or a calibration plot.
