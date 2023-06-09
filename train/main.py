import os
from pathlib import Path

from train.src.ranker import training_pipeline

if __name__ == "__main__":
    training_pipeline("data/sessions.csv", "data/venues.csv", num_folds=os.getenv("TRAIN_FOLDS", 5)).run(
        local_folder=str(Path(".").absolute())
    )
