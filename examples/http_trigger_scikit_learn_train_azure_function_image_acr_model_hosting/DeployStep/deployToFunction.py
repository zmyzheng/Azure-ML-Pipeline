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
from azureml.core.conda_dependencies import CondaDependencies
from azureml.contrib.functions import package, package_http, HTTP_TRIGGER 
from azure.mgmt.containerregistry.v2019_04_01.container_registry_management_client import ContainerRegistryManagementClient
from azure.mgmt.containerregistry.v2019_04_01.models import ImportSourceCredentials, ImportImageParameters, ImportMode
from azure.mgmt.containerregistry.v2019_04_01.models.import_source import ImportSource
from msrestazure.azure_active_directory import ServicePrincipalCredentials

def main():
    # get command-line arguments
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--app_id', type=str, help='app_id for triggering pipeline run, here we use it to re-tag docker image',
                        default='') # app_id for triggering pipeline run, here we use it to re-tag docker image
    parser.add_argument('--app_password', type=str, help='app_password',
                        default='')
    parser.add_argument('--tenant_id', type=str, help='tenant_id',
                        default='')
    parser.add_argument('--registry_password', type=str, help='registry_password',
                        default='')
    args = parser.parse_args()

    # get the Azure ML run object
    run = Run.get_context() 
    ws = run.experiment.workspace

    print("loading model...")
    scikitLearnModel = Model(ws, "ScikitLearnModel")

    print(scikitLearnModel)
    print("model loaded")

    inferenceServerEnv = Environment.from_conda_specification(name = 'InferenceServerEnv', file_path = 'inferenceServerDependency.yml')
    
    inference_config = InferenceConfig(entry_script="score.py", environment=inferenceServerEnv, source_directory="server")

    docker_package = package(ws, [scikitLearnModel], inference_config, functions_enabled=True, trigger=HTTP_TRIGGER)
    docker_package.wait_for_creation(show_output=True)

    # Display the package location/ACR path
    print("docker package created")
    
    print("docker_package.location is: ")
    # Display the package location/ACR path
    print(docker_package.location)

    print("Re-tag image...")

    # docker_registry = docker_package.get_container_registry()  # This method has a bug, so we get password from key vault for now
    registry_name = docker_package.location.split(".")[0]
    registry_uri = docker_package.location.split("/")[0]
    image_tag = docker_package.location.split("/")[1]
    source_registry_credentials =ImportSourceCredentials(password=args.registry_password, username=registry_name)
    source = ImportSource(registry_uri=registry_uri, source_image=image_tag,credentials=source_registry_credentials)

    target_image_tag1 = "inferenceserver:latest"
    target_image_tag2 = "inferenceserver:" + str(scikitLearnModel.version)
    import_parameters = ImportImageParameters(source=source, target_tags=[target_image_tag1, target_image_tag2],untagged_target_repositories=None, mode=ImportMode.force.value )

    app_credentials = ServicePrincipalCredentials(args.app_id, args.app_password, tenant=args.tenant_id)
    client = ContainerRegistryManagementClient(app_credentials, ws.subscription_id)
    registriesOperations = client.registries
    registriesOperations.import_image(resource_group_name=ws.resource_group,registry_name=registry_name,parameters=import_parameters)
    print("The inference image is re-tagged to:")
    print(registry_uri + "/" + target_image_tag1)
    print(registry_uri + "/" + target_image_tag2)

    print("deploy docker image of inference server: done")

if __name__ == "__main__":
    main()