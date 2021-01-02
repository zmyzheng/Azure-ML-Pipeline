from azureml.core.run import Run
import argparse
import os
import pickle
from ScikitLearnTrainer import ScikitLearnTrainer

# get the Azure ML run object
run = Run.get_context()

def main():
    # get command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputDir', type=str, help='input directory',
                        default='processedData')
    parser.add_argument('--outputDir', type=str, help='output directory',
                        default='model')
    
    args = parser.parse_args()

    savePath = args.outputDir
    os.makedirs(savePath, exist_ok=True)

    trainer = ScikitLearnTrainer(args.inputDir)
    model = trainer.train()

    modelFilePath = os.path.join(savePath,"model.pickle")
    pickle.dump(model, open(modelFilePath, 'wb'))


    run.upload_folder(savePath, savePath)
    run.register_model(model_name='SKLearnModel',model_path=modelFilePath)





if __name__ == "__main__":
    main()