#!/usr/bin/env python
# coding: utf-8
import logging
from typing import NoReturn, Optional, Tuple, Union

import pandas as pd
from catboost import CatBoostRanker, Pool
from pandas import DataFrame

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("train.utils")


def calculate_params(data: list) -> Tuple[float, float]:
    """Calculate the mean and standard deviation of a list of numbers.

    Arguments:
        data -- a list of numerical values

    Returns:
        a tuple of two floats: the mean and standard deviation of the data
    """
    # Calculate the mean of the data by summing up all the values and dividing by the length of the list:
    mean = sum(data) / len(data)
    # Calculate the variance of the data by summing up the squared differences between each value and the mean, and dividing by the length of the list:
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    # Calculate the standard deviation of the data by taking the square root of the variance:
    std_dev = variance**0.5
    # Return a tuple of the mean and standard deviation:
    return mean, std_dev


def prepare_datasets(
    train_dataset: DataFrame,
    test_dataset: Optional[DataFrame] = None,
    group_id_name="session_id",
    label_name="purchased",
) -> Tuple[Pool, Union[Pool, None], list]:
    """Prepare datasets for CatBoost model.

    This function takes a train dataset and an optional test dataset and converts them into Pool objects that can be used by CatBoost model.
    It also returns a list of feature names.

    Arguments:
        train_dataset -- a pandas DataFrame containing the train data with features, labels and group ids.

    Keyword Arguments:
        test_dataset -- a pandas DataFrame containing the test data with features, labels and group ids. If None, no test set is used. (default: {None})
        group_id_name -- the name of the column that contains the group ids for ranking. (default: {"session_id"})
        label_name -- the name of the column that contains the binary labels for classification. (default: {"purchased"})

    Raises:
        ValueError: if the train and test datasets have different columns.

    Returns:
        A tuple of (train_set, eval_set, cols), where train_set and eval_set are Pool objects for CatBoost model, and cols is a list of feature names.
    """
    # Get the feature names from the train dataset, excluding the group id and label columns:
    cols = [col for col in train_dataset.columns if col not in [group_id_name, label_name]]

    # Check if the test dataset is provided and has the same columns as the train dataset:
    if test_dataset is not None and set(train_dataset.columns) != set(test_dataset.columns):
        # Raise an error if the columns are different:
        raise ValueError("Сolumns for the train and test datasets should be equals, but they don't!")

    # Create a Pool object from the train dataset with features, labels and group ids:
    train_set = Pool(
        data=train_dataset[cols],
        label=train_dataset[label_name],
        group_id=train_dataset[group_id_name],
    )

    # Create a Pool object from the test dataset with features, labels and group ids if provided:
    if test_dataset is not None:
        eval_set = Pool(
            data=test_dataset[cols],
            label=test_dataset[label_name],
            group_id=test_dataset[group_id_name],
        )
    else:
        # Set eval_set to None if no test dataset is provided:
        eval_set = None

    # Return the tuple of (train_set, eval_set, cols):
    return train_set, eval_set, cols

    python


def train_and_evaluate(
    train_set: Pool,
    eval_set: Optional[Pool],
    names: list,
    ranker: CatBoostRanker,
) -> dict:
    """Train and evaluate a CatBoostRanker model on a given dataset.

    Arguments:
        train_set -- A Pool object containing the training data and labels.
        eval_set -- An optional Pool object containing the validation data and labels.
        names -- A list of strings containing the names of the features.
        ranker -- A CatBoostRanker object that defines the model parameters.

    Returns:
        A dictionary containing the best score, the feature importances and the trained model.
    """
    # Initialize an empty dictionary to store the results:
    results = dict()
    # Initialize an empty dictionary to store the feature importances:
    features = dict()
    # Train the model on the train set and optionally evaluate it on the eval set:
    ranker.fit(train_set, eval_set=eval_set)

    # Get the best score achieved by the model on the eval set:
    results["best_score"] = ranker.get_best_score()

    # Get the feature importances based on the prediction values change metric:
    feature_importances = ranker.get_feature_importance(train_set, "PredictionValuesChange")
    # Loop over the features and their importances:
    for feature, feature_importance in zip(names, feature_importances):
        # Store the feature name and its importance in the features dictionary:
        features[feature] = feature_importance
    # Store the features dictionary in the results dictionary:
    results["feature_importances"] = features
    # Store the trained model in the results dictionary:
    results["model"] = ranker
    # Return the results dictionary:
    return results


def show_results(results: list[dict]) -> NoReturn:
    """Show the results of the cross-validation experiment.

    Arguments:
        results -- a list of dictionaries containing the best scores and feature importances for each fold.

    Returns:
        None. The function prints the results to the log.
    """
    # Extract the MAP@10 values for each fold from the results list:
    map_10 = [result["best_score"]["validation"]["MAP:top=10"] for result in results]
    # Calculate the mean and standard deviation of the MAP@10 values:
    mean, std_dev = calculate_params(map_10)
    # Print a separator line to the log:
    log.info("\n---\n")
    # Print the MAP@10 distribution parameters to the log:
    log.info("MAP@10 distribution parameters:")
    # Format the mean and standard deviation with three decimal places:
    log.info(f"mean = {mean:.3f}, std_dev = {std_dev:.3f}")
    # Calculate and print the 95% confidence interval for the MAP@10 values:
    log.info(f"95% confidence interval from {(mean-2*std_dev):.3f} to {(mean+2*std_dev):.3f}")

    # Loop over the results list and print the best scores and feature importances for each fold:
    for i, result in enumerate(results):
        # Print a separator line to the log:
        log.info("\n---\n")

        # Extract the MAP@10 values for the learn and validation sets from the result dictionary:
        learn = result["best_score"]["learn"]["MAP:top=10"]
        validation = result["best_score"]["validation"]["MAP:top=10"]

        # Print the fold number and the best MAP@10 values for the test and train data to the log:
        log.info(f"Here are results for fold #{i+1} of {len(results)}:")
        log.info(f"Best performer model hit MAP@10 {validation:.3f} for test data, {learn:.3f} for train data")
        # Print an empty line to the log:
        log.info("\n")

        # Extract the feature importances from the result dictionary and sort them by descending order of importance:
        feature_importances = result["feature_importances"]
        feature_importances = sorted(feature_importances.items(), key=lambda pair: pair[1], reverse=True)

        # Print a header line to the log:
        log.info("Feature's importances from the most to the least:\n")
        # Loop over the feature importances and print them to the log with two decimal places:
        for feature, importance in feature_importances:
            log.info(f"importance: {importance:.2f}, feature: {feature}")
