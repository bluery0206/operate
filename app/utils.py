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
from profiles import models as profiles_model

DJANGO_SETTINGS 	= settings
OPERATE_SETTINGS 	= app_model.Setting



def take_image(camera:int, clip_camera:bool, clip_size:int|None=None) -> list[bool, np.ndarray]:
	is_image_taken	= False
	image 			= None
	is_cancelled 	= False

	try:
		cap	= cv2.VideoCapture(camera)
	except BrokenPipeError:
		return [is_image_taken, image]

	while True: 
		try:
			_, frame = cap.read()
			
			if clip_camera and clip_size:
				frame = crop_frame_from_center(frame, clip_size)

			cv2.imshow('"c" to capture | "q" to exit', frame)

			# Quit if X button is pressed
			if cv2.getWindowProperty('"c" to capture | "q" to exit', cv2.WND_PROP_VISIBLE) < 1:
				break

			# Quit
			if (cv2.waitKey(1) & 0XFF == ord('q')):
				is_cancelled = True
				break
			
			# Capture
			if (cv2.waitKey(1) & 0XFF == ord('c')):
				image 			= frame
				is_image_taken 	= True
				break

		except BrokenPipeError:
			break

	cap.release()
	cv2.destroyAllWindows()

	return [is_image_taken, image, is_cancelled]



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
	raw_image_name	= raw_image_path.name
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



def save_embedding(image_path:str|Path) -> bool:
	defset 		= OPERATE_SETTINGS.objects.first()
	
	image_path 	= Path(image_path) if (type(image_path) == str) else image_path
	
	image = open_image(
		image_path 	= image_path, 
		as_gray		= True
	)

	preprocessed_image = preprocess_image(
		image		= image, 
		img_size	= defset.input_size
	)

	embedding = get_image_embedding(preprocessed_image)

	output_name = f'{image_path.stem}.npy'
	output_path = DJANGO_SETTINGS.EMBEDDING_ROOT.joinpath(output_name)

	np.save(output_path, embedding)

	if output_path.exists():
		print(f"Embedding, { str(output_path) } was saved \bSuccessfully\b.")
		return True
	else:
		print(f"Embedding, { str(output_path) } was \bnot saved\b.")
		return False


	
def preprocess_image(image:np.ndarray, img_size:int):
    image = crop_image_from_center(image, True)
    image = cv2.resize(image, dsize=(img_size, img_size))
    image = image / 255.0
    image = np.reshape(image, (1, img_size, img_size ,1))
    image = image.astype(np.float32)

    return image



def get_model():
	model = OPERATE_SETTINGS.objects.first().model
	
	if not model:
		raise FileNotFoundError("There is no model found.")
	
	session_options = ort.SessionOptions()
	session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
	session = ort.InferenceSession(model.path)

	return session



def get_image_embedding(image:np.ndarray):
	model = get_model()
	
	input_name	= model.get_inputs()[0].name
	output_name = model.get_outputs()[0].name
	
	return model.run([output_name], {input_name: image})[0]



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



def format_image_name(image_name):
	return image_name.replace(" ", "_") if " " in image_name else image_name



def search(input_path:Path, threshold:float, search_mode:str):
	defset 		= OPERATE_SETTINGS.objects.first()

	print(f"\nInitiating Facesearch...")
	print(f"Search mode: " + search_mode)

	input = open_image(input_path, True)
	print("Input shape: " + str(input.shape))

	input = preprocess_image(input, img_size=defset.input_size)
	print("Preprocessed input shape: " + str(input.shape))

	if search_mode == "embedding":
		database = list(DJANGO_SETTINGS.EMBEDDING_ROOT.glob("*"))
		database = [np.load(emb_path) for emb_path in database]
	else:
		database = list(DJANGO_SETTINGS.RAW_IMG_ROOT.glob("*"))
		database = [open_image(image_path, True) for image_path in database]
		database = [preprocess_image(image, img_size=defset.input_size) for image in database]

	print(f"Searching...")
	result = search_face(
		inp_image	= input, 
		val_images	= database, 
		threshold	= threshold,
		search_mode	= search_mode
	)

	return result



def search_face(inp_image:np.ndarray, val_images:list[np.ndarray], threshold:float, search_mode:str="embedding"):
	cand_list = []

	inp_emb	= get_image_embedding(inp_image)

	for idx, val in enumerate(val_images):
		if search_mode == "image": 
			val = get_image_embedding(val)

		dist = np.sum(np.square(inp_emb - val), axis=-1)[0]

		if dist <= threshold:
			percentage = get_percentage(threshold, dist)
			cand_list.append([percentage, idx])

			print(f"New candidate found: distance:{dist:.5f}, percentage:{percentage:.2f}")

	print("Total: " + str(len(cand_list)))
	return cand_list if cand_list else None



def get_percentage(threshold:float, distance:float):
	return (1 - (distance/threshold)) * 100



def get_profiles(cand_list:list[np.ndarray], reverse:bool=True, search_mode:str="embedding"):
	if search_mode == "embedding":
		database = list(DJANGO_SETTINGS.EMBEDDING_ROOT.glob("*"))
	else:
		database = list(DJANGO_SETTINGS.RAW_IMG_ROOT.glob("*"))

	database = [str(image_path) for image_path in database]

	cands_dist 	= [float(dist) for dist, idx in cand_list]
	cands_image	= [str(database[idx]) for dist, idx in cand_list]
	
	candidate_profiles = []
	
	for image in cands_image:
		name = Path(image).stem

		personnel	= profiles_model.Personnel.objects.filter(embedding__icontains=name, raw_image__icontains=name, thumbnail__icontains=name).first()
		inmate		= profiles_model.Inmate.objects.filter(embedding__icontains=name, raw_image__icontains=name, thumbnail__icontains=name).first()

		profile = personnel if personnel else inmate

		if profile: candidate_profiles.append(profile)

	result = list(zip(cands_dist, candidate_profiles))
	result = sorted(result, key=lambda x: x[0], reverse=reverse)

	return result

def generate_docx(template_path:str, image_path:str, fields:list[str], data:list[str]):
	doc = Document(template_path)

	# inserts the image
	for p in doc.paragraphs:
		if "[[raw_image]]" in p.text:
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
								run.text = run.text.replace(field, str(value))
								run.font.name = 'Arial'

	file_name	= f"{format_text(data[-1])}.docx"
	if "[[rank]]" in fields:
		file_name	= f"{format_text(data[-5])}_{file_name}"

	save_path	= settings.MEDIA_ROOT.joinpath(file_name)
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



def update_embeddings():
	personnel 	= profiles_model.Personnel.objects.all()
	inmate 		= profiles_model.Inmate.objects.all()

	profiles = list(personnel) + list(inmate)

	
	for profile in profiles:
		print(profile.raw_image.path)
		save_embedding(profile.raw_image.path)
		