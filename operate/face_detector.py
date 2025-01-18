import logging
import numpy as np

from .excepts import *
from .image_handler import crop_image_from_center, resize_image
from .model_loader import get_model

logger = logging.getLogger(__name__)

def get_face(image:np.ndarray) -> np.ndarray:
	try:
		model = get_model("detection")
		logger.debug(model.getInputSize(), exc_info=True)

		# Checking if image is within min and max input shape of the face detector, YuNet
		if image.shape <= (10, 10, 3) or image.shape >= (300, 300, 3) :
			image = crop_image_from_center(image)
			image = resize_image(image, 300)

		# Detection
		result = model.detect(image)

		# Ensuring there's one face in the image
		n_faces = len(result[1:])
		if n_faces == 0: 
			error_message = "No face was detected."
			logger.exception(error_message)
			raise MissingFaceError(error_message)
		elif n_faces > 1: 
			error_message = "Too many faces in an image detected."
			logger.exception(error_message)
			raise TooManyFacesError(error_message)

		# Extracting bounding box and crop face
		bbox = result[1, 0,:4].astype(np.int32)
		face = extract_face_bbox(image, bbox)
		face = crop_image_from_center(face)
	except Exception as e:
		raise e
	else:
		logger.debug("Face retrieved successfuly.", exc_info=True)
		return face
	
def extract_face_bbox(image:np.ndarray, bbox:np.ndarray|list) -> np.ndarray:
	if len(bbox) != 4: 
		error_message = f"Bounding box must contain exactly 4 values (x, y, w, h)."
		logger.exception(error_message)
		raise InvalidBoundingBoxError(error_message)
	
	x, y, w, h = bbox
	return image[y:y+h, x:x+w, :]