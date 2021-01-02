from azureml.core.run import Run
import argparse
import os
from PreProcessor import PreProcessor


# get the Azure ML run object
run = Run.get_context()

def main():
    # get command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, help='input directory',
                        default='sourceData')
    parser.add_argument('--output_dir', type=str, help='output directory',
                        default='processedData')
    
    args = parser.parse_args()

    savePath = args.output_dir
    os.makedirs(savePath, exist_ok=True)

    preProcessor = PreProcessor(args.inputDir)
    X_train, X_test, Y_train, Y_test = preProcessor.process()

    X_train.to_csv(os.path.join(savePath,"X_train.csv"))
    X_test.to_csv(os.path.join(savePath,"X_test.csv"))
    Y_train.to_csv(os.path.join(savePath,"Y_train.csv"))
    Y_test.to_csv(os.path.join(savePath,"Y_test.csv"))
    

    run.upload_folder(savePath, savePath)




if __name__ == "__main__":
    main()
