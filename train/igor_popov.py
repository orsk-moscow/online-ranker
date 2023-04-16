#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from catboost import CatBoostRanker, Pool, cv
from sklearn.model_selection import KFold

from train.utils import prepare_datasets, show_results, train_and_evaluate

RANDOM_STATE = 21
NUM_FOLDS = 2

df_sessions = pd.read_csv("s3/sessions.csv", low_memory=False, index_col=0)
df_sessions.head()
df_sessions.shape
df_venues = pd.read_csv("cache/venues.csv", low_memory=False, index_col=0)
df_venues.head()
df_venues["venue_id"].nunique() == df_venues.shape[0]
df_sessions.session_id.nunique()
df_sessions.session_id.value_counts()
df_sessions[["purchased", "session_id",]].groupby(by="session_id").agg(sum)["purchased"].value_counts(
    sort=False
).reset_index().rename(
    columns={
        "index": "purchased_in_session",
        "purchased": "num_of_sessions",
    }
).sort_values(
    by="purchased_in_session", ascending=True
)
set(df_sessions.venue_id) - set(df_venues.venue_id)
set(df_venues.venue_id) - set(df_sessions.venue_id)
df_sessions.shape[1]
df_all = pd.merge(left=df_sessions, right=df_venues, left_on="venue_id", right_on="venue_id", how="left")
df_sessions.shape[1] + df_venues.shape[1] - 1 == df_all.shape[1]
df_sessions.shape[0] == df_all.shape[0]
df_all["purchased"] = df_all.purchased.astype(int)
df_all.sort_values(by=["session_id", "position_in_list"], ascending=True, inplace=True)
df_all.reset_index(drop=True, inplace=True)
del df_all["position_in_list"]
del df_all["venue_id"]

df_all.head()

sessions = df_all["session_id"].unique()


kf = KFold(n_splits=NUM_FOLDS, shuffle=True, random_state=RANDOM_STATE)
results = []
for train, test in kf.split(sessions):
    sessions_train = set(sessions[train])
    sessions_test = set(sessions[test])
    df_train = df_all[df_all["session_id"].isin(sessions_train)]
    df_test = df_all[df_all["session_id"].isin(sessions_test)]
    train_set, eval_set, names = prepare_datasets(df_train, df_test)
    res = train_and_evaluate(train_set, eval_set, names)
    results.append(res)
show_results(results)

cols_reduced = list(df_all.columns)
cols_reduced.remove("has_seen_venue_in_this_session")
kf = KFold(n_splits=4, shuffle=True, random_state=RANDOM_STATE)
results = []
for train, test in kf.split(sessions):
    sessions_train = set(sessions[train])
    sessions_test = set(sessions[test])
    df_train = df_all[df_all["session_id"].isin(sessions_train)][cols_reduced]
    df_test = df_all[df_all["session_id"].isin(sessions_test)][cols_reduced]
    train_set, eval_set, names = prepare_datasets(df_train, df_test)
    res = train_and_evaluate(train_set, eval_set, names)
    results.append(res)
show_results(results)
