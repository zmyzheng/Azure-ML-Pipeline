import logging
from io.zmyzheng.amlpipeline.HttpTriggeredPipeline import HttpTriggeredPipeline
from azureml.core import Datastore
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import DEFAULT_CPU_IMAGE, RunConfiguration
from azureml.pipeline.steps import EstimatorStep, PythonScriptStep
from azureml.train.sklearn import SKLearn


class HttpSklearnAzureFunctionPipeline(HttpTriggeredPipeline):

    def __init__(self, tenantId, subscriptionId, resourceGroup, amlWorkspaceName, appId, appPassword,
                 storageAccountName, storageAccountKey, computeTargetClusterName,
                 acrPassword,
                 workspaceRegion='eastus',
                 computeTargetVmSize='Standard_NC24s_v3', computeTargetClusterMinNodes=1,
                 computeTargetClusterMaxNodes=4):
        super().__init__(tenantId, subscriptionId, resourceGroup, amlWorkspaceName, appId, appPassword, storageAccountName, storageAccountKey, computeTargetClusterName, workspaceRegion=workspaceRegion, computeTargetVmSize=computeTargetVmSize, computeTargetClusterMinNodes=computeTargetClusterMinNodes, computeTargetClusterMaxNodes=computeTargetClusterMaxNodes)

        # used for re-tag docker image
        self.appId = appId
        self.appPassword = appPassword
        self.tenantId = tenantId
        self.acrPassword = acrPassword


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
        preProcessStep = self.definePreProcessingStep()
        self.steps.append(preProcessStep)
        
        trainStep = self.defineTrainStep()
        trainStep.run_after(preProcessStep)
        self.steps.append(trainStep)

        validationStep = self.defineValidationStep()
        validationStep.run_after(trainStep)
        self.steps.append(validationStep)

        deployStep = self.defineDeploymentStep()
        deployStep.run_after(validationStep)
        self.steps.append(deployStep)


    def definePreProcessingStep(self):
        run_config = RunConfiguration()
        # enable Docker 
        run_config.environment.docker.enabled = True
        # set Docker base image to the default CPU-based image
        run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE
        # use conda_dependencies.yml to create a conda environment in the Docker image for execution
        run_config.environment.python.user_managed_dependencies = False
        # specify CondaDependencies obj
        run_config.environment.python.conda_dependencies = CondaDependencies.create( conda_packages=['pandas, scikit-learn'], pip_packages=['azureml-defaults', 'azureml-contrib-functions', 'azureml-dataprep[pandas,fuse]'])

        preProcessStep = PythonScriptStep( name = "PreProcessing",
                                        script_name="preprocess.py",
                                        arguments=["--inputDir", self.sourceDir, "--outputDir", self.processedDir._output_path_on_compute],
                                        inputs=[self.sourceDir],
                                        outputs=[self.processedDir],
                                        compute_target=self.computeTarget, 
                                        source_directory='PreProcessingStep',
                                        allow_reuse=False,
                                        runconfig=run_config)
        return preProcessStep


    def defineTrainStep(self):
        skLearnEstimator = SKLearn(source_directory='TrainStep',
                            compute_target=self.computeTarget,
                            entry_script='train.py',
                            pip_packages=['azureml-dataprep[pandas,fuse]'],
                            conda_packages = ['pandas']
                            )
        trainStep = EstimatorStep(name="Train", 
                                estimator=skLearnEstimator, 
                                estimator_entry_script_arguments=[ "--inputDir", self.processedDir, "--outputDir", self.modelDir._output_path_on_compute],
                                inputs=[self.processedDir], 
                                outputs=[self.modelDir], 
                                compute_target=self.computeTarget,
                                allow_reuse=False)
        return trainStep

    
    def defineValidationStep(self):
        run_config = RunConfiguration()
        # enable Docker 
        run_config.environment.docker.enabled = True
        # set Docker base image to the default CPU-based image
        run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE
        # use conda_dependencies.yml to create a conda environment in the Docker image for execution
        run_config.environment.python.user_managed_dependencies = False
        # specify CondaDependencies obj
        run_config.environment.python.conda_dependencies = CondaDependencies.create( conda_packages=['pandas, scikit-learn'], pip_packages=['azureml-defaults', 'azureml-contrib-functions', 'azureml-dataprep[pandas,fuse]'])

        validationStep = PythonScriptStep( name = "Validation",
                                        script_name="validate.py",
                                        arguments=["--testDataDir", self.processedDir, "--modelDir", self.modelDir._output_path_on_compute],
                                        inputs=[self.processedDir, self.modelDir],
                                        compute_target=self.computeTarget, 
                                        source_directory='ValidationStep',
                                        allow_reuse=False,
                                        runconfig=run_config)
        return validationStep

    
    def defineDeploymentStep(self):
        run_config = RunConfiguration()
        # enable Docker 
        run_config.environment.docker.enabled = True
        # set Docker base image to the default CPU-based image
        run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE
        # use conda_dependencies.yml to create a conda environment in the Docker image for execution
        run_config.environment.python.user_managed_dependencies = False
        # specify CondaDependencies obj
        run_config.environment.python.conda_dependencies = CondaDependencies.create(pip_packages=['azureml-defaults', 'azureml-contrib-functions'])

        deployStep = PythonScriptStep( name = "Deploy",
                                        #script_name="deployToAppService.py",  # use this line if deploying to App Service
                                        script_name="deployToFunction.py",
                                        arguments=["--app_id", self.appId, "--app_password", self.appPassword, "--tenant_id", self.tenantId, "--registry_password", self.acrPassword],
                                        compute_target=self.computeTarget, 
                                        source_directory='DeployStep',
                                        allow_reuse=False,
                                        runconfig=run_config)
        return deployStep