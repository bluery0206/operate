# Trying out exceptions

class UnrecognizedModelError(Exception): pass
class UnrecognizedColorMode(Exception): pass
class InvalidInputSizeError(Exception): pass
class NoSimilarFaceException(Exception): pass 
class TooManyFacesError(Exception): pass
class InvalidBoundingBoxError(Exception): pass 
class EmbeddingNotSavedException(Exception): pass 
class ImageNotSavedException(Exception): pass 
class InvalidImageFormatError(Exception): pass 
class ProfileNotFoundError(Exception): pass 
class CameraShutdownException(Exception): pass 
class ModelNotFoundError(Exception): pass 
class InvalidProfileType(Exception): pass 
class EmptyDatabase(Exception): pass 

class MissingFaceError(Exception): 
    def __init__(self, *args, profile_id:int|None=None, profile_type:str|None=None):
        super().__init__(*args)
        self.profile_type = profile_type 
        self.profile_id = profile_id


