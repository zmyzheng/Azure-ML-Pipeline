import logging

import json
import os
import pickle
import numpy as np
from azureml.core.model import Model

pipeline = None

def init():
    global pipeline

    modelPath = Model.get_model_path( "ScikitLearnModel")
    pipeline = pickle.load(open(modelPath, 'rb'))



def run(input):
    review = json.loads(input)['review']
    score = pipeline.predict(np.array([review]))[0]

    response = { 'review': review, 'score': score }
    return response