from django.utils import timezone
import onnxruntime as ort
from pathlib import Path 
import numpy as np
import cv2 

from profiles.models import Personnel, Inmate

cwd_path		= Path().cwd()
media_path		= cwd_path.joinpath("media")
database_path 	= media_path.joinpath("raw_images")
searches_path 	= media_path.joinpath("searches")
fs_path			= cwd_path.joinpath("facesearch")
models_path		= fs_path.joinpath("snn_models")


def crop_image_from_center(image):
    height, width = image.shape
    new_dimension = min(height, width)

    left    = int((width   - new_dimension) / 2)
    top     = int((height  - new_dimension) / 2)
    right   = int((width   + new_dimension) / 2)
    bottom  = int((height  + new_dimension) / 2)

    return image[top:bottom, left:right]
 
def format_image_name(image_name):
	return image_name.replace(" ", "_") if " " in image_name else image_name

def get_profiles(cand_list, database_path):
	database = list(database_path.glob("*"))
	database = [str(image_path) for image_path in database]

	cands_dist	= [float(dist) for dist, idx in cand_list]
	cands_image	= [str(database[idx]) for dist, idx in cand_list]
	cands_prof	= []
	
	for image in cands_image:
		# getting image name from full path
		image_name = image.split("\\")[-1]

		personnel	= Personnel.objects.filter(raw_image__endswith=image_name).first()
		inmate		= Inmate.objects.filter(raw_image__endswith=image_name).first()

		# if personnel is not found then the image must be from inmate
		profile = personnel if personnel else inmate

		if profile: cands_prof.append(profile)

	result = list(zip(cands_dist, cands_prof))
	result = sorted(result, reverse=False)

	return result

def search(input_path:Path, database_path:Path, threshold:int=1):
	input = open_gray_image(str(input_path))
	input = preprocess_image(input)

	# fetching and preprocessing database/validation images
	database = list(database_path.glob("*"))
	database = [open_gray_image(str(image_path)) for image_path in database]
	database = [preprocess_image(image) for image in database]

	result = search_face(
		inp_image	= input, 
		val_images	= database, 
		threshold	= threshold
	)

	return result
	
def preprocess_image(image, img_size:int=105):
    cropped_image       = crop_image_from_center(image)
    resize_image        = cv2.resize(cropped_image, dsize=(img_size, img_size))
    normalized_image    = resize_image / 255.0
    reshaped_image      = np.reshape(normalized_image, (1, 105, 105 ,1))
    prep_image			= reshaped_image.astype(np.float32)

    return prep_image

def open_gray_image(image_path):
	return cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

def search_face(inp_image, val_images, threshold):
	session_options = ort.SessionOptions()
	session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
	session = ort.InferenceSession(str(Path().cwd().joinpath("facesearch/snn_models/emb_gen.onnx")))

	input_name	= session.get_inputs()[0].name
	output_name = session.get_outputs()[0].name

	best_cand_dist  = threshold
	best_cand_idx   = None
	cand_list       = []

	inp_emb = session.run([output_name], {input_name: inp_image})[0]

	for idx, val_image in enumerate(val_images):
		val_emb	= session.run([output_name], {input_name: val_image})[0]

		dist	= np.sum(np.square(inp_emb - val_emb), axis=-1)[0]

		if dist <= best_cand_dist:
			best_cand_dist	= dist
			best_cand_idx	= idx
			
			print(f"new candiate: index:{best_cand_idx}, dist:{dist}")

			cand_list.append([best_cand_dist, best_cand_idx])

		if dist <= 0: break

	return cand_list if best_cand_idx else None

def take_image():
	image_name	= None
	camera		= 0
	cap			= cv2.VideoCapture(camera)

	while cap.isOpened(): 
		_, frame = cap.read()
		
		# Cut down frame to 500x500px
		frame_size = 750
		frame = frame[120:120 + frame_size, 200:200 + frame_size, :] # np.ndarray
		
		# Show image back to screen
		cv2.imshow('Image Collection | press "q" to exit', frame)
		
		if cv2.waitKey(10) & 0XFF == ord('q'):
			break
		
		if cv2.waitKey(10) & 0XFF == ord(' '):
			time = timezone.now().strftime("%Y%m%d%H%M%S")
			image_name = f"media/searches/{time}.jpg"
			cv2.imwrite(image_name, frame)
			break
			
	cap.release()
	cv2.destroyAllWindows()
	
	return image_name