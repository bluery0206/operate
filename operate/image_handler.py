from pathlib import Path
from enum import Enum

import logging
import cv2
import numpy as np
	
from app.models import Setting as OPERATE_SETTINGS  
	
from .excepts import *


logger = logging.getLogger(__name__)

class ColorMode(Enum):
	GRAY = 0
	RGB = 1

def open_image(image_path:str, color_mode:ColorMode|None=None) -> np.ndarray:
	try:
		if color_mode == ColorMode.RGB or color_mode == None:
			image = cv2.imread(image_path, cv2.COLOR_BGR2RGB)
		elif color_mode == ColorMode.GRAY:
			image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
		else:
			exception_message = "Color mode unrecognized. Only \"gray\", \"rgb\" and \"bgr\"."
			logger.error(exception_message)
			raise UnrecognizedColorMode(exception_message)
	except FileNotFoundError as e:
		raise e
	else:
		return image
	
	
def resize_image(image:np.ndarray, new_size:int) -> np.ndarray:
	return cv2.resize(image, dsize=(new_size, new_size), interpolation=cv2.INTER_LINEAR)


def crop_image_from_center(image:np.ndarray, is_gray:bool=False) -> np.ndarray:
	if is_gray:
		height, width = image.shape
	else:
		height, width, _ = image.shape

	new_dimension = min(height, width)

	left    = int((width   - new_dimension) / 2)
	top     = int((height  - new_dimension) / 2)
	right   = int((width   + new_dimension) / 2)
	bottom  = int((height  + new_dimension) / 2)

	return image[top:bottom, left:right]


def normalize_image(image:np.ndarray) -> np.ndarray:
	return image / 255.0


def preprocess_input_image(image:np.ndarray) -> np.ndarray:
	defset = OPERATE_SETTINGS.objects.first()
	
	if len(image.shape) >= 3 and image.shape[2] != 1:
		exception_message = f"Invalid image format: expected a grayscale image."
		logger.error(exception_message)
		raise InvalidImageFormatError(exception_message)
	
	if image.shape[:1] is not (defset.input_size, defset.input_size):
		image = crop_image_from_center(image, is_gray=True)
		image = resize_image(image, defset.input_size)
	
	image = crop_image_from_center(image, is_gray=True)
	image = resize_image(image, defset.input_size)
	image = normalize_image(image)
	image = np.reshape(image, (1, defset.input_size, defset.input_size, 1))
	return image.astype(np.float32)

def create_thumbnail(image_path:Path) -> np.ndarray:
	defset = OPERATE_SETTINGS.objects.first()
	logger.debug("Creating thumbnail...")

	try:
		image = open_image(image_path)
		image = crop_image_from_center(image)
		thumbnail = resize_image(image, defset.thumbnail_size)
	except (UnrecognizedColorMode, FileNotFoundError) as e:
		raise e
	else:
		logger.debug("Thumbnail created successfully.")
		return thumbnail

def save_image(image_path:str|Path, image:np.ndarray) -> bool:
	is_saved = cv2.imwrite(str(image_path), image)

	if is_saved:
		logger.debug(f"Saved {image_path.name}...")
		return True
	else:
		exception_message = "Image save operation failed."
		logger.error(exception_message)
		raise ImageNotSavedException(exception_message)



