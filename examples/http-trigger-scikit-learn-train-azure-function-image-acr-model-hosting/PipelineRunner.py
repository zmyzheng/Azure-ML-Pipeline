
import argparse
from HttpSklearnAzureFunctionPipeline import HttpSklearnAzureFunctionPipeline




def main():
    # get command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--tenantId', type=str, help='itenantId',
                        default='')
    parser.add_argument('--subscriptionId', type=str, help='subscriptionId',
                        default='')
    
    parser.add_argument('--resourceGroup', type=str, help='resourceGroup',
                        default='')
    parser.add_argument('--amlWorkspaceName', type=str, help='amlWorkspaceName',
                        default='')
    parser.add_argument('--appId', type=str, help='appId',
                        default='')
    parser.add_argument('--appPassword', type=str, help='appPassword',
                        default='')
    parser.add_argument('--storageAccountName', type=str, help='storageAccountName',
                        default='')
    parser.add_argument('--storageAccountKey', type=str, help='storageAccountKey',
                        default='')
    parser.add_argument('--computeTargetClusterName', type=str, help='computeTargetClusterName',
                        default='')
    parser.add_argument('--acrPassword', type=str, help='acrPassword',
                        default='')
    
    args = parser.parse_args()

    pipeline = HttpSklearnAzureFunctionPipeline(args.tenantId, args.subscriptionId, args.resourceGroup, args.amlWorkspaceName, args.appId, args.appPassword,
                 args.storageAccountName, args.storageAccountKey, args.computeTargetClusterName,
                 args.acrPassword)

    pipeline.registerDataStores()
    pipeline.definePipelineSteps()
    publishedPipeline = pipeline.publishPipeline("TestPipeline", "This is the test pipeline", "1.0.0")
    endpoint = pipeline.exposeHttpTriggeredEndpoint(publishedPipeline, "TestEndpoint", "This is the test endpoint")
    print("The endpoint URL is: " + endpoint)



if __name__ == "__main__":
    main()


