#!/usr/bin/env python
# coding: utf-8
import logging
from pathlib import Path
from typing import NoReturn

import boto3
import botocore.exceptions
import pandas as pd
from catboost import CatBoostRanker
from sklearn.model_selection import KFold

from train.config import RANDOM_STATE, settings
from train.src.utils import prepare_datasets, show_results, train_and_evaluate

logging.basicConfig(level=logging.INFO)


class training_pipeline:
    def __init__(self, sessions: str, venues: str, num_folds: int = 4, *args, **kwargs):
        self._sessions = sessions
        self._venues = venues
        self._log = logging.getLogger("training_pipeline")
        self._num_folds = num_folds

        self._s3_settings = settings.s3
        self._train_settings = settings.train

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
            bagging_temperature=2.0,
            depth=None,
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

        # goal - get the estimates of the MAP@10 metric and avoid overfitting
        kf = KFold(n_splits=self._num_folds, shuffle=True, random_state=RANDOM_STATE)
        results = []
        for train, test in kf.split(sessions):
            sessions_train = set(sessions[train])
            sessions_test = set(sessions[test])
            df_train = df_all[df_all["session_id"].isin(sessions_train)][cols_reduced]
            df_test = df_all[df_all["session_id"].isin(sessions_test)][cols_reduced]
            train_set, eval_set, names = prepare_datasets(df_train, df_test)
            res = train_and_evaluate(train_set, eval_set, names, ranker=self._ranker)
            results.append(res)
        show_results(results)
        best_iteration = max([result["best_score"]["validation"]["MAP:top=10"] for result in results])
        for result in results:
            if result["best_score"]["validation"]["MAP:top=10"] == best_iteration:
                self._best_ranker = result["model"]

    def _save(self) -> NoReturn:
        # TODO Here could be an prerequisites to save the model, e.g. check if the model is better than the previous one.
        self._log.info("Saving model...")
        local_path = Path(".").joinpath(self._train_settings.weights).absolute()
        bucket_name = self._s3_settings.bucket
        self._best_ranker.save_model(str(local_path))
        self._log.info(f"Model saved to local path {local_path}")
        s3_path = f"{self._s3_settings.folder}/{self._s3_settings.weights}"
        self._s3_client.upload_file(str(local_path), bucket_name, s3_path)
        self._log.info(f"Model saved to s3 path {s3_path}")
        local_path.unlink(missing_ok=True)
        self._log.info("Local model deleted.")

    def run(self, local_folder: str = "/opt"):
        self._sessions_local = self._load_data(s3_path=self._sessions, local_folder=local_folder)
        self._venues_local = self._load_data(s3_path=self._venues, local_folder=local_folder)
        self._train()
        self._save()


if __name__ == "__main__":
    training_pipeline("data/sessions.csv", "data/venues.csv", num_folds=5).run(local_folder=str(Path(".").absolute()))
