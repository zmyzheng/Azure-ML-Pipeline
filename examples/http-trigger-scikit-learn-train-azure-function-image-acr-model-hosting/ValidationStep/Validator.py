import os
import pandas as pd
import pickle  
import numpy as np   



class Validator:
    def __init__(self, testDataDir, modelDir):
        self.testDataDir = testDataDir
        self.modelDir = modelDir
    
    def validate(self):
        X_test_Path = os.path.join(self.testDataDir, "X_test.csv")
        Y_test_Path = os.path.join(self.testDataDir, "Y_test.csv")
        model_Path = os.path.join(self.modelDir, "model.pickle")
        pipeline = pickle.load(open(model_Path, 'rb'))

        X_test = pd.read_csv(X_test_Path, dtype=str)["text"]
        Y_test = pd.read_csv(Y_test_Path)["label"]
        Y_test = np.array(Y_test)
        
        Y_predict = pipeline.predict(X_test)

        diff = Y_test - Y_predict

        errorRate = np.sum(np.abs(diff)) / 1.0 / diff.size
        print("error rate: " + errorRate)