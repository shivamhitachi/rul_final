import triton_python_backend_utils as pb_utils
import numpy as np
import joblib
import os

class TritonPythonModel:
    def initialize(self, args):
        model_dir = args['model_repository']
        self.model = joblib.load(os.path.join(model_dir, "1", "model.joblib"))

    def execute(self, requests):
        responses = []
        for request in requests:
            in_tensor = pb_utils.get_input_tensor_by_name(request, "input").as_numpy()
            
            # Predict
            scores = self.model.score_samples(in_tensor).astype(np.float32)
            labels = self.model.predict(in_tensor).astype(np.int32)
            
            # Create output tensors
            out_scores = pb_utils.Tensor("scores", scores)
            out_labels = pb_utils.Tensor("label", labels)
            
            responses.append(pb_utils.InferenceResponse(output_tensors=[out_scores, out_labels]))
        return responses
