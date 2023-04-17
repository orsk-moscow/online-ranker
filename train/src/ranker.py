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

# Define a class for the training pipeline:
class training_pipeline:
    # Define the constructor method with parameters:
    def __init__(self, sessions: str, venues: str, num_folds: int = 4, *args, **kwargs):
        """Initialize the training pipeline object.

        Arguments:
            sessions -- A string that specifies the path to the sessions data file.
            venues -- A string that specifies the path to the venues data file.

        Keyword Arguments:
            num_folds -- An integer that specifies the number of folds for cross-validation (default: {4})
        """
        # Assign the parameters to instance attributes:
        self._sessions = sessions
        self._venues = venues
        # Create a logger object for logging messages:
        self._log = logging.getLogger("training_pipeline")
        # Assign the number of folds to an instance attribute:
        self._num_folds = num_folds

        # Get the S3 settings from the settings module:
        self._s3_settings = settings.s3
        # Get the training settings from the settings module:
        self._train_settings = settings.train

        # Create a S3 client object with the specified credentials and configuration:
        self._s3_client = boto3.client(
            service_name=self._s3_settings.service_name,
            endpoint_url=self._s3_settings.url,
            aws_access_key_id=self._s3_settings.access_key,
            aws_secret_access_key=self._s3_settings.secret_key,
            config=boto3.session.Config(connect_timeout=1, retries={"max_attempts": 0}),
        )

        # Check if the sessions data file exists and is valid:
        self._check_data(sessions)
        # Check if the venues data file exists and is valid:
        self._check_data(venues)

        # Create a CatBoostRanker object with the specified parameters:
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
        """Check if the object exists in the S3 bucket.

        Arguments:
            s3_path -- The path of the object in the S3 bucket.

        Returns:
            True if the object exists, False otherwise.
        """
        # Try to get the metadata of the object:
        try:
            self._s3_client.head_object(Bucket=self._s3_settings.bucket, Key=s3_path)
        # If there is an error, log it and raise it:
        except botocore.exceptions.EndpointConnectionError as e:
            self._log.error(f"The object '{s3_path}' does not exist.")
            raise
        # If there is no error, log that the object exists and return True:
        else:
            self._log.info(f"The object '{s3_path}' exists.")
            return True

    def _load_data(self, s3_path: str, local_folder: str) -> Path:
        """Download the object from the S3 bucket to a local folder.

        Arguments:
            s3_path -- The path of the object in the S3 bucket.
            local_folder -- The path of the local folder where to save the object.

        Returns:
            The path of the downloaded object in the local folder.
        """
        # Get the name of the object from the s3 path:
        name = str(Path(s3_path).name)
        # Construct the local path by joining the local folder and the name:
        local_path = Path(f"{local_folder}/{name}")
        # Create the parent directories of the local path if they do not exist:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        # Delete the local path if it already exists:
        local_path.unlink(missing_ok=True)
        # Log that the data loading is starting:
        self._log.info("Loading data...")
        # Download the object from the S3 bucket to the local path:
        self._s3_client.download_file(
            self._s3_settings.bucket,
            s3_path,
            str(local_path),
        )
        # Log that the data loading is finished:
        self._log.info("Data loaded.")
        # Return the local path of the downloaded object:
        return local_path

    def _train(self) -> NoReturn:
        """Train a model to estimate the Mean Average Precision (MAP) metric on a dataset.

        Raises:
            ValueError: If the venues dataframe does not have unique IDs.
            ValueError: If the merge of the session and venues dataframes is unsuccessful.

        Returns:
            None
        """

        # Load session and venue data from CSV files
        df_sessions = pd.read_csv(self._sessions_local, low_memory=False, index_col=0)
        df_venues = pd.read_csv(self._venues_local, low_memory=False, index_col=0)

        # Check if venue IDs are unique and raise error if not
        if df_venues["venue_id"].nunique() == df_venues.shape[0]:
            self._log.info("Venues is a dictionary.")
        else:
            self._log.error("Venues is not a dictionary.")
            raise ValueError("Venues is not a dictionary.")

        # Merge session and venues dataframes and check if merge was successful
        df_all = pd.merge(left=df_sessions, right=df_venues, left_on="venue_id", right_on="venue_id", how="left")
        if df_sessions.shape[1] + df_venues.shape[1] - 1 == df_all.shape[1] and df_sessions.shape[0] == df_all.shape[0]:
            self._log.info("Data is merged correctly.")
        else:
            self._log.error("Data is not merged correctly.")
            raise ValueError("Data is not merged correctly.")

        # Prepare data for training by converting column types, sorting, and removing unnecessary columns
        df_all["purchased"] = df_all.purchased.astype(int)
        df_all.sort_values(by=["session_id", "position_in_list"], ascending=True, inplace=True)
        df_all.reset_index(drop=True, inplace=True)
        del df_all["position_in_list"]
        del df_all["venue_id"]
        del df_all["has_seen_venue_in_this_session"]

        # Split sessions into training and validation sets using K-fold cross-validation
        sessions = df_all["session_id"].unique()
        cols_reduced = list(df_all.columns)
        kf = KFold(n_splits=self._num_folds, shuffle=True, random_state=RANDOM_STATE)

        # Train and evaluate model on each fold of the cross-validation
        results = []
        for train, test in kf.split(sessions):
            sessions_train = set(sessions[train])
            sessions_test = set(sessions[test])
            df_train = df_all[df_all["session_id"].isin(sessions_train)][cols_reduced]
            df_test = df_all[df_all["session_id"].isin(sessions_test)][cols_reduced]
            train_set, eval_set, names = prepare_datasets(df_train, df_test)
            res = train_and_evaluate(train_set, eval_set, names, ranker=self._ranker)
            results.append(res)

        # Print the results of each fold and store the best model in the _best_ranker attribute
        show_results(results)
        best_iteration = max([result["best_score"]["validation"]["MAP:top=10"] for result in results])
        for result in results:
            if result["best_score"]["validation"]["MAP:top=10"] == best_iteration:
                self._best_ranker = result["model"]

    def _save(self) -> NoReturn:
        """Saves the trained model to both local and S3 paths.

        Args:
            None

        Raises:
            None

        Returns:
            None
        """
        # TODO Here could be an prerequisites to save the model, e.g. check if the model is better than the previous one.
        # Log the saving of the model.
        self._log.info("Saving model...")

        # Get the local path for saving the model.
        local_path = Path(".").joinpath(self._train_settings.weights).absolute()

        # Get the S3 bucket name.
        bucket_name = self._s3_settings.bucket

        # Save the best model to the local path.
        self._best_ranker.save_model(str(local_path))
        self._log.info(f"Model saved to local path {local_path}")

        # Save the best model to the S3 path.
        s3_path = f"{self._s3_settings.folder}/{self._s3_settings.weights}"
        self._s3_client.upload_file(str(local_path), bucket_name, s3_path)
        self._log.info(f"Model saved to s3 path {s3_path}")

        # Delete the local model.
        local_path.unlink(missing_ok=True)
        self._log.info("Local model deleted.")

    def run(self, local_folder: str = "/opt"):
        """Runs the full training and saving process.

        Args:
            local_folder (str): The path to the local folder where the data will be stored. Defaults to '/opt'.

        Raises:
            None

        Returns:
            None
        """
        # Load the sessions and venues data.
        self._sessions_local = self._load_data(s3_path=self._sessions, local_folder=local_folder)
        self._venues_local = self._load_data(s3_path=self._venues, local_folder=local_folder)

        # Train the model.
        self._train()

        # Save the trained model.
        self._save()


if __name__ == "__main__":
    training_pipeline("data/sessions.csv", "data/venues.csv", num_folds=5).run(local_folder=str(Path(".").absolute()))
