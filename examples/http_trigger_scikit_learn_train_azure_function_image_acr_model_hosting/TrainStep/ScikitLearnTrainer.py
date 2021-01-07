import os
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC


class ScikitLearnTrainer:
    def __init__(self, inputDir):
        self.inputDir = inputDir

    def train(self):
        X_train_Path = os.path.join(self.inputDir, "X_train.csv")
        Y_train_Path = os.path.join(self.inputDir, "Y_train.csv")

        X_train = pd.read_csv(X_train_Path, dtype=str)["text"]
        Y_train = pd.read_csv(Y_train_Path)["label"]

        pipeline = make_pipeline(TfidfVectorizer(), LinearSVC())

        pipeline.fit(X_train, Y_train)
        return pipeline