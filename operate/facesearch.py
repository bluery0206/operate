
from django.conf import settings as DJANGO_SETTINGS
from pathlib import Path
import logging
import cv2
import numpy as np

from app.models import Setting as OPERATE_SETTINGS
from profiles import models as profiles_model
from .excepts import *
from . import (
	embedding_generator as emb_gen,
)

logger = logging.getLogger(__name__)

class Facesearch:
    def __init__(self, input_path:Path, model:cv2.FaceDetectorYN, threshold:float=1.0) -> None:
        self.input_path = input_path
        self.model = model
        self.threshold = threshold
        self.search_result = []
            
    def get_percentage(self, distance:float) -> float:
        return (1 - (distance/self.threshold)) * 100

    def get_distance(self, inp_emb, db_emb) -> float:
        return float(np.sum(np.square(inp_emb - db_emb), axis=-1)[0])
        
    def search(self):
        defset = OPERATE_SETTINGS.objects.first()

        try:
            inp_emb = emb_gen.get_image_embedding(self.input_path)
            db_embeddings = list(DJANGO_SETTINGS.EMBEDDING_ROOT.glob("*"))
            db_embeddings = [[emb_path, np.load(emb_path)] for emb_path in db_embeddings]

            while db_embeddings.count() > 0:
                emb_path, db_emb = db_embeddings[0]
                distance = self.get_distance(inp_emb, db_emb)

                if distance <= self.threshold:
                    percentage = self.get_percentage(distance)
                    self.search_result.append([emb_path, distance, percentage])
                    db_embeddings.pop(0)

            if self.search_result.count() == 0:
                error_message = "No matching face detected during the search."
                logger.exception(error_message)
                raise NoSimilarFaceException(error_message)
            
            self.search_result = sorted(self.search_result, key=lambda x: x[1])
        except Exception as e:
            raise e
        else:
            return self.search_result
        
    def get_profiles(self):
        output = []

        try:
            for idx, (emb_path, _, _) in enumerate(self.search_result):
                personnel = profiles_model.Personnel.objects.filter(embedding__icontains=emb_path.name).first()
                inmate = profiles_model.Inmate.objects.filter(embedding__icontains=emb_path.name).first()
                profile = personnel if personnel else inmate

                if profile: 
                    self.search_result[idx][0] = profile
                else:
                    error_message = "Unable to locate the specified profile."
                    logger.exception(error_message)
                    raise ProfileNotFoundError(error_message)
        except Exception as e:
            raise e
        else:
            return self.search_result