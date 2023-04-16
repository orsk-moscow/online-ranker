#!/usr/bin/env python
# coding: utf-8
import logging
from pathlib import Path
from typing import NoReturn

import boto3
import botocore.exceptions
import pandas as pd
from catboost import CatBoostRanker, Pool, cv
from sklearn.model_selection import KFold

from train.config import RANDOM_STATE, settings
from train.utils import calculate_params, prepare_datasets, show_results, train_and_evaluate

logging.basicConfig(level=logging.INFO)


class training_pipeline:
    def __init__(self, sessions: str, venues: str, *args, **kwargs):
        self._sessions = sessions
        self._venues = venues
        self._log = logging.getLogger("training_pipeline")
        self._num_folds = 4

        self._s3_settings = settings.s3
        self._s3_client = boto3.client(
            service_name=self._s3_settings.service_name,
            endpoint_url=self._s3_settings.url,
            aws_access_key_id=self._s3_settings.access_key,
            aws_secret_access_key=self._s3_settings.secret_key,
            config=boto3.session.Config(connect_timeout=1, retries={"max_attempts": 0}),
        )

        self._check_data(sessions)
        self._check_data(venues)

        self._ranker = CatBoostRanker(
            loss_function="YetiRank",
            iterations=4000,
            early_stopping_rounds=100,
            random_state=RANDOM_STATE,
            name="ranker' training",
            eval_metric="MAP:top=10",
            task_type="CPU",
            logging_level="Silent",
            use_best_model=True,
            learning_rate=None,
            random_strength=None,
            ignored_features=None,
            min_data_in_leaf=None,
            min_child_samples=None,
            diffusion_temperature=None,
            bagging_temperature=None,
            depth=None,
            **kwargs,
        )

    def _check_data(self, s3_path) -> bool:
        try:
            self._s3_client.head_object(Bucket=self._s3_settings.bucket, Key=s3_path)
        except botocore.exceptions.EndpointConnectionError as e:
            self._log.error(f"The object '{s3_path}' does not exist.")
            raise
        else:
            self._log.info(f"The object '{s3_path}' exists.")

    def _load_data(self, s3_path: str, local_folder: str) -> Path:
        name = str(Path(s3_path).name)
        local_path = Path(f"{local_folder}/{name}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.unlink(missing_ok=True)
        self._log.info("Loading data...")
        self._s3_client.download_file(
            self._s3_settings.bucket,
            s3_path,
            str(local_path),
        )
        self._log.info("Data loaded.")
        return local_path

    def _train(self) -> NoReturn:
        df_sessions = pd.read_csv(self._sessions_local, low_memory=False, index_col=0)
        df_venues = pd.read_csv(self._venues_local, low_memory=False, index_col=0)
        if df_venues["venue_id"].nunique() == df_venues.shape[0]:
            self._log.info("Venues is a dictionary.")
        else:
            self._log.error("Venues is not a dictionary.")
            raise ValueError("Venues is not a dictionary.")
        df_all = pd.merge(left=df_sessions, right=df_venues, left_on="venue_id", right_on="venue_id", how="left")
        if df_sessions.shape[1] + df_venues.shape[1] - 1 == df_all.shape[1] and df_sessions.shape[0] == df_all.shape[0]:
            self._log.info("Data is merged correctly.")
        else:
            self._log.error("Data is not merged correctly.")
            raise ValueError("Data is not merged correctly.")
        df_all["purchased"] = df_all.purchased.astype(int)
        df_all.sort_values(by=["session_id", "position_in_list"], ascending=True, inplace=True)
        df_all.reset_index(drop=True, inplace=True)
        del df_all["position_in_list"]
        del df_all["venue_id"]
        del df_all["has_seen_venue_in_this_session"]
        sessions = df_all["session_id"].unique()
        cols_reduced = list(df_all.columns)
        cols_reduced.remove("has_seen_venue_in_this_session")

        # test training, goal - get the estimates of the MAP@10 metric
        kf = KFold(n_splits=self._num_folds, shuffle=True, random_state=RANDOM_STATE)
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

        # train on the whole dataset
        train_set = Pool(

    def run(self, local_folder: str = "/opt"):
        self._sessions_local = self._load_data(s3_path=self._sessions, local_folder=local_folder)
        self._venues_local = self._load_data(s3_path=self._venues, local_folder=local_folder)
        self._train()
        self._save()


if __name__ == "__main__":
    training_pipeline("data/sessions.csv", "data/venues.csv").run(local_folder=str(Path(".").absolute()))
