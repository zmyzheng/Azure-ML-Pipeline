# Azure-ML-Pipeline

Azure Machine Learning Pipeline high level API


This project defines a set of high level APIs to define and publish Machine Learning Pipeline from [Azure Machine Learning Service](https://docs.microsoft.com/en-us/azure/machine-learning/).

Azure Machine Learning Service supports 2 types of pipelines:
- Http triggered pipeline: expose a constant REST endpoint to be triggered by authenticated Http request
- Schedule based pipeline: pipeline is triggered by a predefined time interval.


## Use the libary
1. for Http triggered pipeline: inherent [HttpTriggeredPipeline](https://github.com/zmyzheng/Azure-ML-Pipeline/blob/main/zmyzheng/amlpipeline/HttpTriggeredPipeline.py) class and override two methods:registerDataStores() and definePipelineSteps() . Example: [HttpSklearnAzureFunctionPipeline.py](https://github.com/zmyzheng/Azure-ML-Pipeline/blob/main/examples/http_trigger_scikit_learn_train_azure_function_image_acr_model_hosting/HttpSklearnAzureFunctionPipeline.py)
2. for schedule based pipeline: (developing)


## Build locally

### Use conda (recommended)
<code>
conda create -p .env python=3.7

conda activate ./.env

.env/bin/pip install -r src/requirements.txt
</code>



### Use pip
<code>
python3.6 -m venv .env

source .env/bin/activate

.env/bin/pip install -r src/requirements.txt
</code>