#!/usr/bin/env python
# coding: utf-8
import logging
from typing import NoReturn, Optional, Tuple, Union

import pandas as pd
from catboost import CatBoostRanker, Pool
from pandas import DataFrame

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("train.utils")


def calculate_params(data):
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = variance**0.5
    return mean, std_dev


def prepare_datasets(
    train_dataset: DataFrame,
    test_dataset: Optional[DataFrame] = None,
    group_id_name="session_id",
    label_name="purchased",
) -> Tuple[Pool, Union[Pool, None], list]:
    cols = [col for col in train_dataset.columns if col not in [group_id_name, label_name]]

    if test_dataset is not None and set(train_dataset.columns) != set(test_dataset.columns):
        raise ValueError("Сolumns for the train and test datasets should be equals, but they don't!")

    train_set = Pool(
        data=train_dataset[cols],
        label=train_dataset[label_name],
        group_id=train_dataset[group_id_name],
    )

    if test_dataset is not None:
        eval_set = Pool(
            data=test_dataset[cols],
            label=test_dataset[label_name],
            group_id=test_dataset[group_id_name],
        )
    else:
        eval_set = None

    return train_set, eval_set, cols


def train_and_evaluate(
    train_set: Pool,
    eval_set: Optional[Pool],
    names: list,
    ranker: CatBoostRanker,
) -> dict:
    results = dict()
    features = dict()
    ranker.fit(train_set, eval_set=eval_set)

    results["best_score"] = ranker.get_best_score()

    feature_importances = ranker.get_feature_importance(train_set, "PredictionValuesChange")
    for feature, feature_importance in zip(names, feature_importances):
        features[feature] = feature_importance
    results["feature_importances"] = features
    results["model"] = ranker

    return results


def show_results(results: list[dict]) -> NoReturn:
    map_10 = [result["best_score"]["validation"]["MAP:top=10"] for result in results]
    mean, std_dev = calculate_params(map_10)
    log.info("\n---\n")
    log.info("MAP@10 distribution parameters:")
    log.info(f"mean = {mean:.3f}, std_dev = {std_dev:.3f}")
    log.info(f"95% confidence interval from {(mean-2*std_dev):.3f} to {(mean+2*std_dev):.3f}")

    for i, result in enumerate(results):
        log.info("\n---\n")

        learn = result["best_score"]["learn"]["MAP:top=10"]
        validation = result["best_score"]["validation"]["MAP:top=10"]

        log.info(f"Here are results for fold #{i+1} of {len(results)}:")
        log.info(f"Best performer model hit MAP@10 {validation:.3f} for test data, {learn:.3f} for train data")
        log.info("\n")

        feature_importances = result["feature_importances"]
        feature_importances = sorted(feature_importances.items(), key=lambda pair: pair[1], reverse=True)

        log.info("Feature's importances from the most to the least:\n")
        for feature, importance in feature_importances:
            log.info(f"importance: {importance:.2f}, feature: {feature}")
