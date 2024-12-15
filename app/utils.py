from django.http import HttpResponse
from django.conf import settings
from pathlib import Path
from docx.shared import Inches
from docx import Document
import string


from django.utils import timezone
import onnxruntime as ort
from pathlib import Path 
import numpy as np
from django.db.models import Q
import cv2 

# from profiles.models import Personnel, Inmate
from app import models as app_model

OPERATE_SETTINGS = app_model.Setting
INP_SIZE = 105


CWD_PATH	= Path().cwd()

FS_PATH		= CWD_PATH.joinpath("facesearch")
MED_PATH 	= CWD_PATH.joinpath("media")

SNN_PATH	= FS_PATH.joinpath(f"snn_models")

EMB_PATH	= MED_PATH.joinpath(f"embeddings")
RAW_PATH	= MED_PATH.joinpath(f"raw_images")



def take_image(camera, crop_camera:int|None=None, crop_size:int|None=None):
	is_image_taken	= False
	image 			= None

	try:
		cap	= cv2.VideoCapture(int(camera))
	except BrokenPipeError:
		return [is_image_taken, image]

	while cap.isOpened(): 
		try:
			_, frame = cap.read()
			
			if crop_camera and crop_size:
				frame = crop_frame_from_center(frame, crop_size)

			cv2.imshow('"c" to capture | "q" to exit', frame)

			# Quit if X button is pressed
			if cv2.getWindowProperty('"c" to capture | "q" to exit', cv2.WND_PROP_VISIBLE) < 1:
				break

			# Quit
			if (cv2.waitKey(1) & 0XFF == ord('q')):
				break
			
			# Capture
			if (cv2.waitKey(1) & 0XFF == ord('c')):
				image = frame

			if image:
				is_image_taken 	= True
				break

		except BrokenPipeError:
			break

	cap.release()
	cv2.destroyAllWindows()

	return [is_image_taken, image]



def crop_frame_from_center(frame, new_size):
	return frame[120:120 + new_size, 200:200 + new_size, :]



def open_image(image_path:str|Path, as_gray:bool=False) -> np.ndarray:
	if as_gray:
		return cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
	else:
		return cv2.imread(str(image_path))



def save_image(image_path:str|Path, image:np.ndarray) -> bool:
	return cv2.imwrite(str(image_path), image)



def create_thumbnail(raw_image_path:Path, thumbnail_size):
	raw_image_name	= str(raw_image_path).split("\\")[-1]
	raw_image		= open_image(raw_image_path)

	print(f"Raw Image: {"Found" if raw_image is not None else "Not found"}, {raw_image_name = }")

	cropped_image = crop_image_from_center(raw_image)
	resized_image = resize_image(cropped_image, thumbnail_size)

	return resized_image



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



def resize_image(image_array, new_size) :
        return cv2.resize(image_array, dsize=(new_size, new_size))



def save_embedding(inp_path:str|Path):
	is_saved = False

	if type(inp_path) == str:
		inp_path = Path(inp_path) 
	
	inp_image = open_image(
		image_path 	= inp_path, 
		as_gray		= True
	)

	inp_image = preprocess_image(
		image		= inp_image, 
		img_size	= INP_SIZE
	)

	inp_emb = get_image_embedding(inp_image)

	inp_name = str(inp_path).split("\\")[-1].split(".")[0]
	emb_name = f'{inp_name}.npy'

	np.save(EMB_PATH.joinpath(emb_name), inp_emb)

	exists = True if len(list(EMB_PATH.glob(emb_name))) > 0 else False

	if exists:
		is_saved = True
		print(f"Array saved: {str(list(EMB_PATH.glob(emb_name))[0])}")

	return [is_saved, emb_name, inp_emb]


	
def preprocess_image(image:np.ndarray, img_size:int):
    image = crop_image_from_center(image, True)
    image = cv2.resize(image, dsize=(img_size, img_size))
    image = image / 255.0
    image = np.reshape(image, (1, img_size, img_size ,1))
    image = image.astype(np.float32)

    return image



def get_image_embedding(image:np.ndarray):
	model = OPERATE_SETTINGS.objects.first().model
	
	if not model:
		raise FileNotFoundError("There is no model found.")
	
	session_options = ort.SessionOptions()
	session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
	session = ort.InferenceSession(model.path)
	
	input_name	= session.get_inputs()[0].name
	output_name = session.get_outputs()[0].name

	return session.run([output_name], {input_name: image})[0]



def get_full_name(profile:object, m_initial:bool=True) -> str:
	full_name = profile.l_name.title()

	if profile.f_name:
		full_name += f", {profile.f_name.title()}"

	if profile.m_name and m_initial:
		full_name += f" {profile.m_name[0]}."
	elif profile.m_name:
		full_name += f" {profile.m_name.title()}"

	if profile.suffix:
		full_name += f" {profile.suffix}"

	return full_name

def format_text(text:str) -> str:
	text    = text.strip()
	symbols = string.punctuation.replace('_', ' ')
	translation_table = str.maketrans(symbols, '_' * len(symbols))

	text = text.replace(",", "")
	text = text.translate(translation_table)
	return text

def generate_docx(template_path:str, image_path:str, fields:list[str], data:list[str]) -> list[str]:
	doc = Document(template_path)

	# inserts the image
	for p in doc.paragraphs:
		if "raw_image" in p.text:
			p.clear()
			run = p.add_run()
			run.add_picture(
				image_path, 
				width=Inches(2), 
				height=Inches(2)
			)
			p.alignment = 1

	# fills in the table
	for table in doc.tables:
		for row in table.rows:
			cell = row.cells[1]
			
			for paragraph in cell.paragraphs:
				for field, value in zip(fields, data):
					if field in paragraph.text:
						for run in paragraph.runs:
							if field in run.text:
								run.text        = run.text.replace(field, str(value))
								run.font.name   = 'Arial'

	file_name	= f"{format_text(data[-1])}.docx"
	
	if "[[rank]]" in fields:
		rank        = format_text(data[-5])
		file_name	= rank + "_" + file_name

	save_path = settings.MEDIA_ROOT.joinpath(file_name)
	doc.save(save_path)

	return [file_name, save_path]

def save_file(file_name:str, save_path:Path):
	with open(save_path, 'rb') as f:
		response = HttpResponse(
			f.read(),
			content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
		)
		response['Content-Disposition'] = f'attachment; filename="{file_name}"'
	
	save_path.unlink()

	return response

def format_image_name(image_name):
	return image_name.replace(" ", "_") if " " in image_name else image_name

# def get_profiles(cand_list, reverse=True, by_array:bool=False):

# 	# Get dataset from path
# 	database = list(EMB_PATH.glob("*")) if by_array else list(RAW_PATH.glob("*"))
# 	database = [str(image_path) for image_path in database]
# 	print(f"get_profiles(): {len(database) = }")

# 	# Getting profiles
# 	cands_dist 	= [float(dist) for dist, idx in cand_list]
# 	cands_image	= [str(database[idx]) for dist, idx in cand_list]

# 	# Candidates profiles
# 	cands_prof	= []
	
# 	for image in cands_image:

# 		# extracting imagename.ext from full path
# 		embedding_name = image.split("\\")[-1]
# 		name = embedding_name.split(".")[0]

# 		print(f"get_profiles(): {embedding_name = }")


# 		if by_array:
# 			personnel 	= Personnel.objects.filter(embedding__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()
# 			inmate		= Inmate.objects.filter(embedding__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()
# 		else:
# 			personnel 	= Personnel.objects.filter(raw_image__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()
# 			inmate		= Inmate.objects.filter(raw_image__endswith=embedding_name, raw_image__icontains=name, thumbnail__icontains=name).first()

# 		# if personnel is not found then the image must be from inmate
# 		profile = personnel if personnel else inmate

# 		if profile: cands_prof.append(profile)

# 	result = list(zip(cands_dist, cands_prof))
# 	result = sorted(result, key=lambda x: x[0], reverse=reverse)

# 	return result

# def search(input_path:Path,  threshold:int=1, by_array:bool=False):
# 	input = open_gray_image(str(input_path))
# 	# print(f"\nfacesearch(): {input.shape = }")

# 	input = preprocess_image(input, img_size=INP_SIZE)
# 	print(f"facesearch(): preprocess_image(): {input.shape = }")

# 	# print(f"facesearch(): input_image: {"Found" if input_image is not None else "Not found."}")
# 	# print(f"facesearch(): {input_image.shape = }")
	
# 	if by_array:
# 		database = list(EMB_PATH.glob("*"))
# 		print(f"facesearch(): by_array: {len(database) = }")
	
# 		database = [np.load(emb_path) for emb_path in database]
# 		print(f"facesearch(): by_array: {len(database) = }")
# 	else:
# 		# fetching and preprocessing database/validation images
# 		database = list(RAW_PATH.glob("*"))
# 		print(f"facesearch(): {len(database) = }")
	
# 		database = [open_gray_image(str(image_path)) for image_path in database]
# 		print(f"facesearch(): open_gray_image(): {len(database)  = }")
	
# 		database = [preprocess_image(image, img_size=INP_SIZE) for image in database]
# 		print(f"facesearch(): preprocess_image(): {len(database)  = }")

# 	result = search_face(
# 		inp_image	= input, 
# 		val_images	= database, 
# 		threshold	= threshold,
# 		by_array	= by_array
# 	)

# 	return result

# def update_image_embeddings():
# 	personnels 	= Personnel.objects.all()
# 	inmates 	= Inmate.objects.all()

# 	data = list(personnels) + list(inmates)

# 	if not data:
# 		return False

# 	print(f"Creating embedding from image using model: {OPERATE_SETTINGS.objects.first().model.name}")

# 	for profile in data:
# 		# print(f"Personnel: {profile}, raw_image_path: {profile.raw_image.path}")
# 		is_image_saved, emb_name, inp_emb = save_embedding(profile.raw_image.path)

# 		if not is_image_saved:
# 			print(f"Personnel: {profile} embedding was not generated.")
# 			continue
		
# 		profile.embedding = f"embeddings/{emb_name}"

# 		profile.save()

# 	return True

# def search_face(inp_image, val_images, threshold, by_array:bool=False, break_in_zero:bool=True):
# 	best_cand_dist  = threshold
# 	best_cand_idx	= None
# 	cand_list       = []

# 	inp_emb	= get_image_embedding(inp_image)

# 	for idx, val in enumerate(val_images):

# 		# if not array meaning the search method was image and
# 		# so the image needs to be processed and get its embedding
# 		if not by_array: 
# 			val = get_image_embedding(val)

# 		# dist = np.sum(np.square(inp_emb - val), axis=-1)[0]
# 		dist = np.sum(np.square(inp_emb - val), axis=-1)

# 		# print(f"search_face(): dist:{dist}, database_idx:{idx}, threshold:{threshold}")

# 		if dist <= threshold:
# 			best_cand_dist	= dist
# 			best_cand_idx	= idx
# 			print(f"search_face(): New candidate found: dist:{dist}, threshold:{threshold}")

# 			cand_list.append([get_percentage(threshold, dist), best_cand_idx])

# 		# if break_in_zero and dist <= 0: break

# 	return cand_list if cand_list else None


# def get_percentage(threshold, best_cand_dist):
# 	return (1 - (best_cand_dist/threshold)) * 100

# 

# def save_image(image_path, image):
# 	return cv2.imwrite(image_path, image)


	