from enum import Enum

import logging
import cv2
import onnxruntime as ort

from app.models import Setting as OPERATE_SETTINGS  
from .excepts import *

logger = logging.getLogger(__name__)

class ModelType(Enum):
	RECOGNITION = 0
	DETECTION = 1

def get_model(type:ModelType):
	defset = OPERATE_SETTINGS.objects.first()
	logger.debug(f"Getting {type} model...", exc_info=True)
	
	try:
		match type:
			case 0:
				session_options = ort.SessionOptions()
				session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
				model = ort.InferenceSession(defset.model_recognition.path, sess_options=session_options)
			case 1:
				model = cv2.FaceDetectorYN.create(
					model = defset.model_detection.path,
					config = "",
					input_size = (defset.clip_size, defset.clip_size)
				)
			case _:
				error_message = f"No model represents \"{type}\"."
				logger.error(error_message, exc_info=True)
				raise UnrecognizedModelError(error_message)
	except FileNotFoundError as e:
		logger.error(str(e), exc_info=True)
		raise e
	else:
		logger.debug(f"{type.capitalize()} model retrieved successfuly.", exc_info=True)
		return model