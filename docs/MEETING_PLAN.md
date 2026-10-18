# Five-Meeting Plan (60 minutes each)

**Roles that rotate every meeting:** Driver (shares screen and types), Navigator (reads the task aloud and checks it), Scribe (updates the decisions log in `docs/DECISIONS.md`). Work in pairs for the hands-on blocks. If the team is small, one person per task is fine.

**Rule for every meeting:** the last 5 minutes are always commit, push, and assign. No one leaves without a named task and a due date (24 hours before the next meeting).

---

## Meeting 1: Load, inspect, and agree on definitions

**Goal:** everyone has a working environment and has verified the data. We agree how Form is defined.
**Notebook:** `notebooks/01_load_and_inspect.ipynb`

| Min | Activity |
|---|---|
| 0-5 | State the two questions: *Analysis* (what is associated with outcomes) and *Prediction* (what we can know before kickoff). Explain why they need different data handling. |
| 5-15 | **Setup check.** Everyone clones the repo, creates the venv, installs requirements, and runs cell 1. Everyone must see shape `(760, 13)` before moving on. Fix problems now. |
| 15-30 | **Data checks (pairs).** Write code for each check below and confirm the result:<br>1. `df.dtypes` and `df.isna().sum()`: any missing values?<br>2. `df['team'].value_counts()`: should be 20 teams with 38 rows each.<br>3. `df.groupby('match_id').size()`: every match has exactly 2 rows.<br>4. `df.groupby('match_id')['possession_pct'].sum()`: every match sums to 100.<br>5. Merge each row with its opponent's row. Confirm one team's `xg` equals the other's `xgc`.<br>6. `df[['xg','xgc','possession_pct']].describe()`: do the min and max look plausible? |
| 30-45 | **First look (3 pairs, one variable each).** Pair A: `xg`. Pair B: `xgc`. Pair C: `possession_pct`. Each pair makes (a) the mean by `result` using `groupby`, and (b) a boxplot by result, with titles and axis labels. Everyone also computes the share of matches won by the home team. |
| 45-55 | **Define Form on the whiteboard.** Agree on and write in `docs/DECISIONS.md`: *Form = total points from the team's previous 5 matches, using earlier matches only, never the current one.* Decide what happens to each team's first 5 matches (answer: exclude them, which leaves 660 rows). Discuss why the current match must not leak in. Also note that the two rows of each match mirror each other, so they are not independent observations. |
| 55-60 | Commit the notebook. Assign the tasks below. |

**Tasks due before Meeting 2**
- Person/pair 1: write `add_form(df)` in `src/features.py`. It returns the DataFrame with a `form` column. Hint: sort by team and date, then `groupby('team')` with `shift(1)` and a rolling window.
- Person/pair 2: write `add_rolling_features(df, window=5)` in `src/features.py`. It adds `roll_xg`, `roll_xgc`, `roll_possession` as the mean of the previous 5 matches only.
- Person/pair 3: write a short `check_features(df)` with assertions, such as: the first 5 matches of every team have NaN form, and form is always between 0 and 15.
- Person/pair 4: write `src/plots.py` with a reusable `boxplot_by_result(df, column)` function.

---

## Meeting 2: Features and exploration

**Goal:** a trusted feature table and a first full set of plots.
**Notebook:** `notebooks/02_features_and_eda.ipynb`

| Min | Activity |
|---|---|
| 0-10 | Open each pull request and read it aloud. Merge only after one other person approves. |
| 10-25 | **Hand-check Form.** Pick one team (Leicester City) and compute the form for matchweek 6 by hand from the first 5 results. Compare to the code output. Repeat for a second team. Run `check_features`. Do not move on until the hand check matches. |
| 25-35 | Build `analysis_df` by dropping rows with missing form. Confirm it has 660 rows. Save the logic in `src/features.py`, not in the notebook. |
| 35-52 | **Exploration (pairs).** Pair A: histograms of all four variables. Pair B: boxplots of all four variables by result (use the helper). Pair C: a correlation heatmap of the four variables, plus home-vs-away averages. Each pair writes one sentence on what stands out. |
| 52-60 | Commit. Assign tasks. |

**Tasks due before Meeting 3**
- Pair A: Kruskal-Wallis test of each variable across W/D/L, plus Spearman correlation of each variable with `points`.
- Pair B: logistic regression (win vs not win) with standardized predictors, using statsmodels.
- Pair C: variance inflation factors for the four predictors, and a one-paragraph discussion of what the correlation heatmap implies.

---

## Meeting 3: Analysis (explaining outcomes)

**Goal:** answer the Analysis question with statistics we can defend.
**Notebook:** `notebooks/03_analysis.ipynb`
**Note:** here `xg`, `xgc`, and `possession_pct` are same-match values. That is fine for explaining outcomes. Form is pre-match.

| Min | Activity |
|---|---|
| 0-10 | Review the Kruskal-Wallis and Spearman results. State each p-value and effect direction aloud. |
| 10-30 | **Logistic regression review.** Fit `Logit(win ~ form + xg + xgc + possession_pct)` on standardized predictors. Because each match appears twice, use cluster-robust standard errors: `.fit(cov_type='cluster', cov_kwds={'groups': df['match_id']})`. Report odds ratios with 95% confidence intervals for each variable. |
| 30-40 | **Robustness check.** Rerun using only the home team's row (380 matches, no duplicate matches). Do the conclusions change? |
| 40-55 | **Interpretation.** Each person writes three plain-English sentences for one variable: direction, size, and caveat. Read them out, then merge into `docs/FINDINGS.md`. Rule: write "associated with", not "causes". |
| 55-60 | Commit. Assign tasks. |

**Tasks due before Meeting 4**
- Pair A: build the match-level modelling table (one row per match, home team's features minus away team's features, target = home result). Use only pre-match features: `form` and the `roll_*` columns.
- Pair B: write `evaluate(y_true, proba)` in `src/models.py` returning accuracy, log loss, and a confusion matrix.
- Pair C: write the chronological split function: sort by date, first 220 matches train, last 110 matches test.

---

## Meeting 4: Prediction

**Goal:** a fair, leakage-free model and an honest evaluation.
**Notebook:** `notebooks/04_prediction.ipynb`

| Min | Activity |
|---|---|
| 0-10 | Confirm the modelling table has 330 matches (matchweeks 6 to 38). Confirm no column uses the current match's own stats. Everyone explains why the same-match `xg` cannot be a feature here. |
| 10-20 | **Baselines.** Compute accuracy and log loss for (a) always predicting the home win and (b) predicting the class frequencies in the training set. Every model must beat these. |
| 20-35 | **Model.** Standardize on the training set only, fit multinomial `LogisticRegression` on the four difference features, and evaluate on the test set with `evaluate()`. |
| 35-48 | **Drop-one analysis.** Refit with each predictor removed in turn and compare test log loss. Make a bar chart of the four results. |
| 48-55 | **Leakage audit.** Each person picks one feature and traces how it was computed, line by line, to confirm only earlier matches are used. |
| 55-60 | Commit. Assign tasks. |

**Tasks due before Meeting 5**
- Pair A: confusion matrix plot and a paragraph on which outcome (win, draw, loss) the model predicts worst. Draws are usually hardest.
- Pair B: a 95% interval for the test accuracy, using the binomial standard error `sqrt(p*(1-p)/n)`, with n = 110.
- Pair C: a draft README results section and a limitations list.

---

## Meeting 5: Reproduce and present

**Goal:** another person can reproduce everything, and we can present it clearly.

| Min | Activity |
|---|---|
| 0-15 | **Clean-clone test.** One person who did not write the code clones the repo into a new folder, creates a new venv, installs requirements, and runs every notebook with *Restart and Run All*. Fix every error found. |
| 15-25 | Confirm the numbers in the README and `docs/FINDINGS.md` match the notebook outputs exactly. |
| 25-45 | **Presentation rehearsal.** Use this 6-part structure, about 1 minute each: (1) the question, (2) the data and variable definitions, (3) the method and how we avoided leakage, (4) analysis results, (5) prediction results against baselines, (6) limitations. Run it once through with a timer, then give feedback. |
| 45-55 | Limitations pass. Confirm these are covered: one season and one league; one provider's xG model; a small test set (110 matches), so accuracy has a wide interval; association rather than causation. |
| 55-60 | Tag the final commit (`git tag v1.0`) and confirm every deliverable is in the repo. |

**Final deliverables:** the four notebooks, `src/` code, `docs/FINDINGS.md`, a completed README, and the presentation.
