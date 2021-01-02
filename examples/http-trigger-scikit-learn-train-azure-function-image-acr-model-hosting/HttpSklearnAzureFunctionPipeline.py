import logging
from io.zmyzheng.aml_pipeline.HttpTriggeredPipeline import HttpTriggeredPipeline
from azureml.core import Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, RunConfiguration
from azureml.pipeline.steps import EstimatorStep, PythonScriptStep


class HttpSklearnAzureFunctionPipeline(HttpTriggeredPipeline):

    def __init__(self, tenantId, subscriptionId, resourceGroup, amlWorkspaceName, appId, appPassword,
                 storageAccountName, storageAccountKey, computeTargetClusterName,
                 arcPassword,
                 workspaceRegion='eastus',
                 computeTargetVmSize='Standard_NC24s_v3', computeTargetClusterMinNodes=1,
                 computeTargetClusterMaxNodes=4):
        super().__init__(tenantId, subscriptionId, resourceGroup, amlWorkspaceName, appId, appPassword, storageAccountName, storageAccountKey, computeTargetClusterName, workspaceRegion=workspaceRegion, computeTargetVmSize=computeTargetVmSize, computeTargetClusterMinNodes=computeTargetClusterMinNodes, computeTargetClusterMaxNodes=computeTargetClusterMaxNodes)

        self.arcPassword = arcPassword


    def registerDataStores(self):
        sourceDs = Datastore.register_azure_blob_container(workspace=self.ws, 
            datastore_name='SourceBlob', 
            container_name="SourceBlob",
            account_name=self.storageAccountName, 
            account_key=self.storageAccountKey,
            create_if_not_exists=True)
    
        self.sourceDir = DataReference(sourceDs, 
                    data_reference_name='sourceData', 
                    path_on_datastore=None, 
                    mode='mount', 
                    path_on_compute=None, 
                    overwrite=False)

        processedDs = Datastore.register_azure_blob_container(workspace=self.ws, 
            datastore_name='ProcessedBlob', 
            container_name="ProcessedBlob",
            account_name=self.storageAccountName, 
            account_key=self.storageAccountKey,
            create_if_not_exists=True)

        self.processedDir = PipelineData(name="processedData", 
                                datastore=processedDs, 
                                output_mode='upload',  
                                is_directory=True,
                                output_overwrite=True,
                                output_path_on_compute='processedData')
        
        modelDs = Datastore.register_azure_blob_container(workspace=self.ws, 
            datastore_name='ModelBlob', 
            container_name="ModelBlob",
            account_name=self.storageAccountName, 
            account_key=self.storageAccountKey,
            create_if_not_exists=True)

        self.modelDir = PipelineData(name="model", 
                                datastore=modelDs, 
                                output_mode='upload',  
                                is_directory=True,
                                output_overwrite=True,
                                output_path_on_compute='model')
    


    def definePipelineSteps(self):
        logging.info("Define AML Pipeline Steps...")

        self.steps.append(self.preProcessingStep())


    def preProcessingStep(self):
        run_config = RunConfiguration()
        # enable Docker 
        run_config.environment.docker.enabled = True
        # set Docker base image to the default CPU-based image
        run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE
        # use conda_dependencies.yml to create a conda environment in the Docker image for execution
        run_config.environment.python.user_managed_dependencies = False
        # specify CondaDependencies obj
        run_config.environment.python.conda_dependencies = CondaDependencies.create( conda_packages=['pandas, scikit-learn'], pip_packages=['azureml-defaults', 'azureml-contrib-functions', 'azureml-dataprep[pandas,fuse]'])

        preProcessStep = PythonScriptStep( name = "PreProcessingStep",
                                        script_name="preprocess.py",
                                        arguments=["--input_dir", self.sourceDir, "--output_dir", "processedData"],
                                        inputs=[self.sourceDir],
                                        outputs=[self.processedDir],
                                        compute_target=self.computeTarget, 
                                        source_directory='PreProcessingStep',
                                        allow_reuse=False,
                                        runconfig=run_config)
        return preProcessStep
