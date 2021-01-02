from __future__ import print_function, division

import time
import os
import copy
import argparse
import sys
from os import listdir

from azureml.core.model import Model
from azureml.core.run import Run
from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig



def main():
    # get the Azure ML run object
    run = Run.get_context() 
    ws = run.experiment.workspace

    print("loading model...")
    scikitLearnModel = Model(ws, "ScikitLearnModel")
    
    print(scikitLearnModel)
 
    
    print("model loaded")

    inferenceServerEnv = Environment.from_conda_specification(name = 'InferenceServerEnv',
                                             file_path = 'inferenceServerDependency.yml')
    
    inference_config = InferenceConfig(entry_script="score.py", environment=inferenceServerEnv, source_directory="server")
    docker_package = Model.package(ws, [scikitLearnModel], inference_config, image_name="inferenceserver", image_label=str(scikitLearnModel.version))
    docker_package = Model.package(ws, [scikitLearnModel], inference_config, image_name="inferenceserver", image_label="latest")

    docker_package.wait_for_creation(show_output=True)
    # Display the package location/ACR path
    print("docker package created")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("docker_package.location is: ")
    print(docker_package.location)
    print(docker_package)
    print("deploy docker image of inference server: done")

if __name__ == "__main__":
    main()