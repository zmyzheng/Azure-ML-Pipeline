from azureml.core.run import Run
import argparse
import os
from Validator import Validator


# get the Azure ML run object
run = Run.get_context()

def main():
    # get command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--testDataDir', type=str, help='test data directory',
                        default='processedData')
    parser.add_argument('--modelDir', type=str, help='model directory',
                        default='model')
    
    args = parser.parse_args()



    validator = Validator(args.testDataDir, args.modelDir)
    validator.validate()



if __name__ == "__main__":
    main()
