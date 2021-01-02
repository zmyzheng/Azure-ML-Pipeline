import abc

import argparse
import json
import logging
import os
import shutil
import sys
import time

from azureml.core import Datastore, Experiment, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.compute_target import ComputeTargetException
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.dataset import Dataset
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, RunConfiguration
from azureml.data.data_reference import DataReference
from azureml.exceptions import ProjectSystemException
from azureml.pipeline.core import Pipeline, PipelineData, PipelineEndpoint
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import EstimatorStep, PythonScriptStep
from azureml.train.dnn import PyTorch


class AMLPipeline(metaclass=abc.ABCMeta):
    def __init__(self, tenantId, subscriptionId, resourceGroup, amlWorkspaceName, appId, appPassword,
                 storageAccountName, storageAccountKey, computeTargetClusterName,
                 workspaceRegion='eastus',
                 computeTargetVmSize='Standard_NC24s_v3', computeTargetClusterMinNodes=1,
                 computeTargetClusterMaxNodes=4):

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        self.__initWorkSpace(tenantId, subscriptionId, resourceGroup, amlWorkspaceName, workspaceRegion,
                                       appId, appPassword)

        self.__initComputeCluster(computeTargetClusterName, computeTargetVmSize,
                                                       computeTargetClusterMinNodes, computeTargetClusterMaxNodes)
        
        self.storageAccountKey = storageAccountKey
        self.storageAccountName = storageAccountName
        self.steps = []

    def __initWorkSpace(self, tenantId, subscriptionId, resourceGroup, amlWorkspaceName, workspaceRegion, appId,
                        appPassword):
        try:
            svc_pr = ServicePrincipalAuthentication(
                tenant_id=tenantId,
                service_principal_id=appId,
                service_principal_password=appPassword)
        except ProjectSystemException as err:
                    # Usually because authentication didn't work
                    logging.error('Authentication did not work.')
                    logging.error('ProjectSystemException')
                    raise err
        try:
            self.ws = Workspace(subscription_id=subscriptionId,
                           resource_group=resourceGroup,
                           workspace_name=amlWorkspaceName,
                           auth=svc_pr)
            logging.info("Found workspace {} at location {} using Azure CLI \
                    authentication".format(self.ws.name, self.ws.location))
            # Need to create the workspace
        except Exception as err:
            self.ws = Workspace.create(name=amlWorkspaceName,
                                  subscription_id=subscriptionId,
                                  resource_group=resourceGroup,
                                  create_resource_group=True,
                                  location=workspaceRegion,  # Or other supported Azure region
                                  auth=svc_pr)
            logging.info("Created workspace {} at location {}".format(self.ws.name, self.ws.location))


    def __initComputeCluster(self, computeTargetClusterName, computeTargetVmSize, computeTargetClusterMinNodes,
                             computeTargetClusterMaxNodes):
        try:
            self.computeTarget = ComputeTarget(workspace=self.ws, name=computeTargetClusterName)
            logging.info('Found existing compute target.')
        except ComputeTargetException:
            logging.info('Creating a new compute target...')
            # AML Compute config - if max_nodes are set, it becomes persistent storage that scales
            compute_config = AmlCompute.provisioning_configuration(vm_size=computeTargetVmSize,
                                                                   min_nodes=computeTargetClusterMinNodes,
                                                                   max_nodes=computeTargetClusterMaxNodes)
            # create the cluster
            self.computeTarget = ComputeTarget.create(self.ws, computeTargetClusterName, compute_config)
            self.computeTarget.wait_for_completion(show_output=True)


    @abc.abstractmethod
    def registerDataStores(self):
        pass

    @abc.abstractmethod
    def definePipelineSteps(self):
        pass

    def publishPipeline(self, pipelineName, pipelineDescription, pipelineVersion):
        pipeline = Pipeline(workspace=self.ws, steps=self.steps)
        logging.info("Validating Pipeline...")
        pipeline.validate()
        logging.info("Pipeline validation complete")

        logging.info("Publishing new pipeline...")
        publishedPipeline = pipeline.publish(
            name=pipelineName, description=pipelineDescription, version=pipelineVersion)
        return publishedPipeline

    