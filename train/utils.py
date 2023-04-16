#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from catboost import CatBoostRanker, Pool, cv
from sklearn.model_selection import KFold

from train.config import RANDOM_STATE


def calculate_params(data):
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std_dev = variance**0.5
    return mean, std_dev


def prepare_datasets(train_dataset, test_dataset, group_id_name="session_id", label_name="purchased"):
    if set(train_dataset.columns) != set(test_dataset.columns):
        raise ValueError("Сolumns for the train and test datasets should be equals, but they don't!")
    cols = [col for col in train_dataset.columns if col not in [group_id_name, label_name]]

    train_set = Pool(
        data=train_dataset[cols],
        label=train_dataset[label_name],
        group_id=train_dataset[group_id_name],
    )

    eval_set = Pool(
        data=test_dataset[cols],
        label=test_dataset[label_name],
        group_id=test_dataset[group_id_name],
    )
    return train_set, eval_set, cols


def train_and_evaluate(train_set, eval_set, ranker, names, i, NUM_FOLDS):
    results = dict()
    features = dict()
    ranker.fit(train_set, eval_set=eval_set)

    results["best_score"] = ranker.get_best_score()

    feature_importances = ranker.get_feature_importance(train_set, "PredictionValuesChange")
    for feature, feature_importance in zip(names, feature_importances):
        features[feature] = feature_importance
    results["feature_importances"] = features

    filename = f"model_iteration_{i+1}_of_{NUM_FOLDS}.cbm"
    ranker.save_model(filename)
    results["best_model_weights_file"] = filename

    return results


def show_results(results):
    map_10 = [result["best_score"]["validation"]["MAP:top=10"] for result in results]
    mean, std_dev = calculate_params(map_10)
    print("MAP@10 distribution parameters:")
    print(f"mean = {mean:.3f}, std_dev = {std_dev:.3f}")
    print(f"95% confidence interval from {(mean-2*std_dev):.3f} to {(mean+2*std_dev):.3f}")
    for i, result in enumerate(results):
        print("\n---\n")

        learn = result["best_score"]["learn"]["MAP:top=10"]
        validation = result["best_score"]["validation"]["MAP:top=10"]
        print(f"Here are results for fold #{i+1} of {len(results)}:")
        print(f"Best performer model hit MAP@10 {validation:.3f} for test data, {learn:.3f} for train data")
        print()
        feature_importances = result["feature_importances"]
        feature_importances = sorted(feature_importances.items(), key=lambda pair: pair[1], reverse=True)
        print("Feature's importances from the most to the least:\n")
        for feature, importance in feature_importances:
            print(f"importance: {importance:.2f}, feature: {feature}")
