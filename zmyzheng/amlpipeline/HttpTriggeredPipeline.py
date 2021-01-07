
import logging
from zmyzheng.amlpipeline.AMLPipeline import AMLPipeline
from azureml.pipeline.core import PipelineEndpoint

class HttpTriggeredPipeline(AMLPipeline):

    def exposeHttpTriggeredEndpoint(self, publishedPipeline, endpointName, endpointDescription):
        logging.info("Expose unchanged pipeline endpoint URL...")

        pipelineEndpoint = None
        try:
            pipelineEndpoint = PipelineEndpoint.get(workspace=self.ws, name=endpointName)
            logging.info("PipelineEndpoint with name " + endpointName + " already exists")
            logging.info("Add newly published pipeline to this PipelineEndpoint...")
            pipelineEndpoint.add(publishedPipeline)
            logging.info("Set newly published pipeline as the default pipeline...")
            pipelineEndpoint.set_default(publishedPipeline)
            logging.info("Pipeline Endpoint URL: {}".format(pipelineEndpoint.endpoint))
        except Exception as err:
            logging.info(
                "PipelineEndpoint with name " + endpointName + "  does not exist, will create an PipelineEndpoint with name:  " + endpointName + "  for the newly published pipeline...")
            pipelineEndpoint = PipelineEndpoint.publish(workspace=self.ws, name=endpointName,
                                                         pipeline=publishedPipeline,
                                                         description=endpointDescription)
            logging.info("PipelineEndpoint with name " + endpointName + " created for the newly published pipeline")
            logging.info("Pipeline Endpoint URL: {}".format(pipelineEndpoint.endpoint))
        return pipelineEndpoint.endpoint