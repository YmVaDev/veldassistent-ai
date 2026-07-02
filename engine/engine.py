
class Engine:

    def __init__(self):
        self.models = []

    def add_model(self, model):
        self.models.append(model)

    def process(self, image_path):

        detections = []
        observation = None

        for model in self.models:

            result = model.process(image_path)

            if observation is None:
                observation = result["observation"]

            detections.extend(result["detections"])

        return {
            "success": True,
            "api_version": "1.0",

            "observation": observation,

            "summary": {
                "count": len(detections)
            },

            "detections": detections
        }