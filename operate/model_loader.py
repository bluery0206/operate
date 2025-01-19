from enum import Enum

import logging
import cv2
import onnxruntime as ort

from app.models import Setting as OPERATE_SETTINGS  
from .excepts import *

logger = logging.getLogger(__name__)

class ModelType(Enum):
	EMBEDDING_GENERATOR = 0
	DETECTION = 1
	DETECTION_AS_ONNX = 2

def get_model(type:ModelType):
	defset = OPERATE_SETTINGS.objects.first()
	logger.debug(f"Getting {type}...")

	
	try:
		if type == ModelType.EMBEDDING_GENERATOR:
			if not defset.model_embedding_generator: 
				raise ModelNotFoundError("Embedding Generator model not found.")
			
			session_options = ort.SessionOptions()
			session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
			model = ort.InferenceSession(defset.model_embedding_generator.path, sess_options=session_options)
		elif type == ModelType.DETECTION:
			if not defset.model_detection: 
				raise ModelNotFoundError("Face Detection model not found.")
			
			model = cv2.FaceDetectorYN.create(
				model = defset.model_detection.path,
				config = "",
				input_size = (defset.clip_size, defset.clip_size)
			)
		elif type == ModelType.DETECTION_AS_ONNX:
			if not defset.model_detection: 
				raise ModelNotFoundError("Face Detection model not found.")
			
			session_options = ort.SessionOptions()
			session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
			model = ort.InferenceSession(defset.model_detection.path, sess_options=session_options)
		else:
			exception_message = f"No model represents \"{type}\"."
			logger.exception(exception_message)
			raise UnrecognizedModelError(exception_message)
	except FileNotFoundError as e:
		raise e
	else:
		logger.debug(f"{type} model retrieved successfuly.")
		return model