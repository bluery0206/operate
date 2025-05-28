from pathlib import Path
from django.conf import settings as DJANGO_SETTINGS 

import logging
import cv2
import numpy as np

from app.models import Setting as OPERATE_SETTINGS

from .excepts import *
from operate import (
    model_loader as mload,
    image_handler as imhand,
    face_detector as facedet,
	embedding_generator as emb_gen
)

logger = logging.getLogger(__name__)


def get_image_embedding(image:Path, face_det_model=None, emb_gen_model=None) -> np.ndarray:
    defset = OPERATE_SETTINGS.objects.first()

    try:
        image = imhand.open_image(image, imhand.ColorMode.RGB)
        
        if image.shape[:2] is not (defset.bbox_size, defset.bbox_size):
            image = imhand.crop_image_from_center(image)
            image = imhand.resize_image(image, defset.bbox_size)
                    
        image = facedet.get_face(image, face_det_model)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = imhand.preprocess_input_image(image)
        embedding = emb_gen.generate_embedding(image, emb_gen_model)
    except Exception as e :
        raise e
    else:
        return embedding


def generate_embedding(image:np.ndarray, model=None) -> np.ndarray:
    try: 
        model = model if model else mload.get_model(mload.ModelType.EMBEDDING_GENERATOR)
        input_name = model.get_inputs()[0].name
        output_name = model.get_outputs()[0].name
    except Exception as e:
        raise e
    else:
        return model.run([output_name], {input_name: image})[0]

    
def save_embedding(embedding:np.ndarray, name:str, p_type:str) -> bool:
    logger.debug(f"Saving embedding: p_type={p_type}, name={name}...")
    if p_type == "personnel":
        output_path = DJANGO_SETTINGS.EMBEDDING_PERSONNEL.joinpath(name + '.npy')
    elif p_type == "inmate":
        output_path = DJANGO_SETTINGS.EMBEDDING_INMATE.joinpath(name + '.npy')
    else:
        exception_message = "Invalid `p_type` detected."
        logger.exception(exception_message)
        raise InvalidProfileType(exception_message)

    np.save(output_path, embedding)

    if output_path.exists():
        logger.debug("Embedding saved successfully.")
        return True
    else:
        exception_message = "Failed to save the embedding to the specified location."
        logger.exception(exception_message)
        raise EmbeddingNotSavedException(exception_message)

    
def update_embeddings() -> None:
    from profiles.models import Personnel, Inmate

    logger.debug("Updating embeddings...")
    
    # Caching the models to reduce search time due to model reinitialization unlike previous logic
    logger.debug("Retreiving models for embedding generation and face detection...")
    emb_gen_model = mload.get_model(mload.ModelType.EMBEDDING_GENERATOR)
    face_det_model = mload.get_model(mload.ModelType.DETECTION)
    logger.debug("Model retreived successfully...")

    personnel = Personnel.objects.all()
    inmate = Inmate.objects.all()
    profiles = list(personnel) + list(inmate)

    for profile in profiles:
        image_path = Path(profile.raw_image.path)

        try:
            embedding = get_image_embedding(image_path, face_det_model, emb_gen_model)
            save_embedding(embedding, image_path.stem, profile.p_type)
            logger.debug(f"Image: {image_path.name} successfully saved.")
        except MissingFaceError as e:
            raise MissingFaceError(e, profile_id=profile.pk, profile_type=profile.p_type)
        except Exception as e:
            raise e

    logger.debug("Profile image embeddings successfully updated.")