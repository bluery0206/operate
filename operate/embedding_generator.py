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
from operate import (
    model_loader as mload,
    image_handler as imhand,
    face_detector as facedet,
	embedding_generator as emb_gen
)

logger = logging.getLogger(__name__)

def get_image_embedding(image:Path) -> np.ndarray:
    defset = OPERATE_SETTINGS.objects.first()

    try:
        image = imhand.open_image(image, imhand.ColorMode.RGB)
        
        if image.shape[:1] is not (defset.bbox_size, defset.bbox_size):
            image = imhand.crop_image_from_center(image, is_gray=True)
            image = imhand.resize_image(image, defset.bbox_size)
                    
        image = facedet.get_face(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = imhand.preprocess_input_image(image)
        embedding = emb_gen.generate_embedding(image)
    except Exception as e :
        raise e
    else:
        return embedding

def generate_embedding(image:np.ndarray) -> np.ndarray:
    try: 
        model = get_model("recognition")
        input_name = model.get_inputs()[0].name
        output_name = model.get_outputs()[0].name
    except Exception as e:
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
        logger.exception(error_message)
        raise EmbeddingNotSavedException(error_message)
    
def update_embeddings() -> None:
	personnel = profiles.Personnel.objects.all()
	inmate = profiles.Inmate.objects.all()
	profiles = list(personnel) + list(inmate)

	for profile in profiles:
		save_embedding(profile.raw_image.path)
		