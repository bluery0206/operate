from pathlib import Path
from django.conf import settings as DJANGO_SETTINGS 

import logging
import cv2
import numpy as np

from app.models import Setting as OPERATE_SETTINGS

from .excepts import *
from .image_handler import open_image, preprocess_input_image
from .model_loader import get_model
from .face_detector import get_face

logger = logging.getLogger(__name__)

def get_image_embedding(image_path:Path):
    try:
        image = open_image(image_path, "rgb")
        image = get_face(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = preprocess_input_image(image)
        embedding = generate_embedding(image)
    except (UnrecognizedColorMode, FileNotFoundError, UnrecognizedModelError, InvalidImageFormatError) as e :
        raise e
    else:
        return embedding

def generate_embedding(image:np.ndarray) -> np.ndarray:
    try: 
        model = get_model("recognition")
        input_name = model.get_inputs()[0].name
        output_name = model.get_outputs()[0].name
    except (UnrecognizedModelError, FileNotFoundError) as e:
        raise e
    else:
        return model.run([output_name], {input_name: image})[0]
    
def save_embedding(embedding:np.ndarray, name:str) -> bool:
    output_path = DJANGO_SETTINGS.EMBEDDING_ROOT.joinpath(name + '.npy')
    np.save(output_path, embedding)

    if output_path.exists():
        logger.debug("Embedding saved successfully.", exc_info=True)
        return True
    else:
        error_message = "Failed to save the embedding to the specified location."
        logger.error(error_message, exc_info=True)
        raise EmbeddingNotSavedException(error_message)