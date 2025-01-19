# For the detection model
# @article{wu2023yunet,
#  title={Yunet: A tiny millisecond-level face detector},
#  author={Wu, Wei and Peng, Hanyang and Yu, Shiqi},
#  journal={Machine Intelligence Research},
#  volume={20},
#  number={5},
#  pages={656--665},
#  year={2023},
#  publisher={Springer}
# }

import logging
import numpy as np

from app.models import Setting as OPERATE_SETTINGS
from .excepts import *
from . import (
	model_loader as mload,
	image_handler as imhand,
)

logger = logging.getLogger(__name__)

def get_face(image:np.ndarray) -> np.ndarray:
	defset = OPERATE_SETTINGS.objects.first()
	
	try:
		model = mload.get_model(mload.ModelType.DETECTION)
		logger.debug(f"Model input: {model.getInputSize()}")

		# Checking if image is within min and max input shape of the face detector, YuNet
		if image.shape <= (10, 10, 3) or image.shape >= (300, 300, 3) :
			image = imhand.crop_image_from_center(image)
			image = imhand.resize_image(image, defset.bbox_size)

		# Detection
		result = model.detect(image)[1:]
		
		# Ensuring there's one face in the image
		if len(result) > 1: 
			exception_message = "Too many faces in an image detected."
			logger.exception(exception_message)
			raise TooManyFacesError(exception_message)
		elif result[0] is None: 
			exception_message = "No face was detected."
			logger.exception(exception_message)
			raise MissingFaceError(exception_message)

		# Extracting bounding box and crop face
		bbox = result[0][0][:4].astype(np.int32)
		face = extract_face_bbox(image, bbox)
		face = imhand.crop_image_from_center(face)
	except Exception as e:
		raise e
	else:
		logger.debug("Face retrieved successfuly.")
		return face
	
def extract_face_bbox(image:np.ndarray, bbox:np.ndarray|list) -> np.ndarray:
	if len(bbox) != 4: 
		exception_message = f"Bounding box must contain exactly 4 values (x, y, w, h)."
		logger.exception(exception_message)
		raise InvalidBoundingBoxError(exception_message)
	
	x, y, w, h = bbox
	return image[y:y+h, x:x+w, :]