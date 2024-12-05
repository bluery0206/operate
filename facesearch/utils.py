from django.utils import timezone
import onnxruntime as ort
from pathlib import Path 
import numpy as np
from django.db.models import Q
import logging
import cv2 

from profiles.models import Personnel, Inmate
from settings.models import OperateSetting


CWD_PATH	= Path().cwd()

FS_PATH		= CWD_PATH.joinpath("facesearch")
MED_PATH 	= CWD_PATH.joinpath("media")

SNN_PATH	= FS_PATH.joinpath(f"snn_models")

EMB_PATH	= MED_PATH.joinpath(f"embeddings")
RAW_PATH	= MED_PATH.joinpath(f"raw_images")


def format_image_name(image_name):
	return image_name.replace(" ", "_") if " " in image_name else image_name


def get_profiles(cand_list, reverse=True, by_array:bool=False):

	# Get dataset from path
	database = list(EMB_PATH.glob("*")) if by_array else list(RAW_PATH.glob("*"))
	database = [str(image_path) for image_path in database]
	print(f"get_profiles(): {len(database) = }")

	# Getting profiles
	cands_dist 	= [float(dist) for dist, idx in cand_list]
	cands_image	= [str(database[idx]) for dist, idx in cand_list]

	# Candidates profiles
	cands_prof	= []
	
	for image in cands_image:

		# extracting imagename.ext from full path
		embedding_name = image.split("\\")[-1]
		name = embedding_name.split(".")[0]

		print(f"get_profiles(): {embedding_name = }")


		if by_array:
			personnel 	= Personnel.objects.filter(embedding__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()
			inmate		= Inmate.objects.filter(embedding__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()
		else:
			personnel 	= Personnel.objects.filter(raw_image__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()
			inmate		= Inmate.objects.filter(raw_image__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()

		# if personnel is not found then the image must be from inmate
		profile = personnel if personnel else inmate

		if profile: cands_prof.append(profile)

	result = list(zip(cands_dist, cands_prof))
	result = sorted(result, key=lambda x: x[0], reverse=reverse)

	return result

def search(input_path:Path,  threshold:int=1, by_array:bool=False):
	input = open_gray_image(str(input_path))
	print(f"\nfacesearch(): {input.shape = }")

	input = preprocess_image(input)
	print(f"facesearch(): preprocess_image(): {input.shape = }")

	# print(f"facesearch(): input_image: {"Found" if input_image is not None else "Not found."}")
	# print(f"facesearch(): {input_image.shape = }")
	
	if by_array:
		database = list(EMB_PATH.glob("*"))
		print(f"facesearch(): by_array: {len(database) = }")
	
		database = [np.load(emb_path) for emb_path in database]
		print(f"facesearch(): by_array: {len(database) = }")
	else:
		# fetching and preprocessing database/validation images
		database = list(RAW_PATH.glob("*"))
		print(f"facesearch(): {len(database) = }")
	
		database = [open_gray_image(str(image_path)) for image_path in database]
		print(f"facesearch(): open_gray_image(): {len(database)  = }")
	
		database = [preprocess_image(image) for image in database]
		print(f"facesearch(): preprocess_image(): {len(database)  = }")

	result = search_face(
		inp_image	= input, 
		val_images	= database, 
		threshold	= threshold,
		by_array	= by_array
	)

	return result

def update_image_embeddings():
	personnels 	= Personnel.objects.all()
	inmates 	= Inmate.objects.all()

	data = list(personnels) + list(inmates)

	if not data:
		return False

	print(f"Creating embedding from image using model: {OperateSetting.objects.first().model.name}")

	for profile in data:
		# print(f"Personnel: {profile}, raw_image_path: {profile.raw_image.path}")
		is_image_saved, emb_name, inp_emb = save_embedding(profile.raw_image.path)

		if not is_image_saved:
			print(f"Personnel: {profile} embedding was not generated.")
			continue
		
		profile.embedding = f"embeddings/{emb_name}"

		profile.save()

	return True

def search_face(inp_image, val_images, threshold, by_array:bool=False, break_in_zero:bool=True):
	best_cand_dist  = threshold
	best_cand_idx	= None
	cand_list       = []

	inp_emb	= get_image_embedding(inp_image)

	for idx, val in enumerate(val_images):

		# if not array meaning the search method was image and
		# so the image needs to be processed and get its embedding
		if not by_array: 
			val = get_image_embedding(val)

		# dist = np.sum(np.square(inp_emb - val), axis=-1)[0]
		dist = np.sum(np.square(inp_emb - val), axis=-1)

		print(f"search_face(): dist:{dist}, database_idx:{idx}")

		if dist <= best_cand_dist:
			best_cand_dist	= dist
			best_cand_idx	= idx
			# print(f"search_face(): New candidate found: dist:{dist}, database_idx:{idx}")

			cand_list.append([get_percentage(threshold, dist), best_cand_idx])

		if break_in_zero and dist <= 0: break

	return cand_list if cand_list else None
	
def preprocess_image(image, img_size:int=105):
    cropped_image       = crop_image_from_center(image, True)
    resize_image        = cv2.resize(cropped_image, dsize=(img_size, img_size))
    normalized_image    = resize_image / 255.0
    reshaped_image      = np.reshape(normalized_image, (1, 105, 105 ,1))
    prep_image			= reshaped_image.astype(np.float32)

    return prep_image

def open_gray_image(image_path):
	return cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

def open_image(image_path):
	return cv2.imread(str(image_path))

def get_percentage(threshold, best_cand_dist):
	return (1 - (best_cand_dist/threshold)) * 100

def crop_frame_from_center(frame, new_size):
	return frame[120:120 + new_size, 200:200 + new_size, :]

def take_image(camera, crop_frame:int|None=None, new_size:int|None=None):
	print(f"\nOpening opencv camera using cam: {camera}...")

	is_image_taken	= False
	image 			= None

	try:
		cap	= cv2.VideoCapture(int(camera))
	except BrokenPipeError:
		logging.error("Client disconnected before response was fully sent.")

	while cap.isOpened(): 
		_, frame = cap.read()
		
		frame = crop_frame_from_center(frame, new_size) if crop_frame and new_size else frame

		# Show frame back to screen
		cv2.imshow('OPERATE | Image Capture | "c" to capture | "q" to exit', frame)

		# Quit
		if (cv2.waitKey(1) & 0XFF == ord('q')):
			break
		
		# Capture
		if (cv2.waitKey(1) & 0XFF == ord('c')):
			is_image_taken 	= True
			image 			= frame
			break

	cap.release()
	cv2.destroyAllWindows()

	return [is_image_taken, image]

def save_image(image_path, image):
	return cv2.imwrite(image_path, image)

def get_image_embedding(inp_image):
	model = OperateSetting.objects.first().model
	
	if not model:
		raise FileNotFoundError("There is no model found.")
	
	# print(f"Creating embedding from image using model: {model.name}")

	session_options = ort.SessionOptions()
	session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
	session = ort.InferenceSession(model.path)
	
	input_name	= session.get_inputs()[0].name
	output_name = session.get_outputs()[0].name

	return session.run([output_name], {input_name: inp_image})[0]

def create_thumbnail(raw_image_path, new_size):
	raw_image_name	= str(raw_image_path).split("\\")[-1]
	raw_image		= cv2.imread(raw_image_path)

	print(f"create_thumbnail(): Raw Image: {"Found" if raw_image is not None else "Not found"}")
	print(f"create_thumbnail(): {raw_image_name = }")

	cropped_image = crop_image_from_center(raw_image)
	resized_image = resize_image(cropped_image, new_size)

	print(f"create_thumbnail(): Crop: {"Successful" if cropped_image is not None else "Unsuccessful"}")
	print(f"create_thumbnail(): Resize: {"Successful" if resized_image is not None else "Unsuccessful"}")

	return resized_image

def resize_image(image_array, new_size) :
        return cv2.resize(image_array, dsize=(new_size, new_size))

def crop_image_from_center(image, is_gray=False):
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

def save_embedding(inp_path:str|Path):
	inp_path = Path(inp_path)
	# print(f"save_embedding(): {str(inp_path) = }")

	inp_image	= open_gray_image(inp_path)
	# print(f"save_embedding(): open_gray_image: {inp_image.shape = }")

	inp_image	= preprocess_image(inp_image)
	# print(f"save_embedding(): preprocess_image: {inp_image.shape = }")

	inp_emb = get_image_embedding(inp_image)
	# print(f"save_embedding(): get_image_embedding: {inp_emb.shape = }")

	inp_name = str(inp_path).split("\\")[-1].split(".")[0]
	# print(f"save_embedding(): {inp_name = }")

	emb_name = f'{inp_name}.npy'

	np.save(EMB_PATH.joinpath(emb_name), inp_emb)

	exists = True if len(list(EMB_PATH.glob(emb_name))) > 0 else False

	print(f"Array saved: {str(list(EMB_PATH.glob(emb_name))[0])}")

	is_saved = True if exists else False 

	return [is_saved, emb_name, inp_emb]
	