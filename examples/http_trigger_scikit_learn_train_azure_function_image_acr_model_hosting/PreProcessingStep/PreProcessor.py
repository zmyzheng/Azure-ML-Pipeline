import os
import pandas as pd
from sklearn.model_selection import train_test_split


class PreProcessor:
    def __init__(self, inputDir):
        self.inputDir = inputDir

    def process(self):
        filePath = os.path.join(self.inputDir, "reviews.csv")
        data = pd.read_csv(filePath, dtype=str)
        X = data["text"]
        Y = data["label"]
        X_train, X_test, Y_train, Y_test = train_test_split( X, Y, test_size=0.25, random_state=42)
        return X_train, X_test, Y_train, Y_test
