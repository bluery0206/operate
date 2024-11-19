from django.utils import timezone
import onnxruntime as ort
from pathlib import Path 
import numpy as np
import logging
import cv2 

from profiles.models import Personnel, Inmate

# MODEL_NAME = "emb_gen.onnx"
MODEL_NAME = "2024.11.16.02.52.onnx"

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


def get_profiles(cand_list, database_path, reverse=True):
	database = list(database_path.glob("*"))
	database = [str(image_path) for image_path in database]

	cands_dist 	= [float(dist) for dist, idx in cand_list]
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
	result = sorted(result, key=lambda x: x[0], reverse=reverse)

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

def get_percentage(threshold, best_cand_dist):
	return (1 - (best_cand_dist/threshold)) * 100

def search_face(inp_image, val_images, threshold):

	best_cand_dist  = threshold
	best_cand_idx   = None
	cand_list       = []

	inp_emb	= get_image_embedding(MODEL_NAME, inp_image)

	for idx, val_image in enumerate(val_images):
		val_emb	= get_image_embedding(MODEL_NAME, val_image)

		dist	= np.sum(np.square(inp_emb - val_emb), axis=-1)[0]

		if dist <= best_cand_dist:
			best_cand_dist	= dist
			best_cand_idx	= idx
			
			print(f"new candiate: index:{best_cand_idx}, dist:{dist}")

			cand_list.append([get_percentage(threshold, dist), best_cand_idx])

		if dist <= 0: break

	return cand_list if cand_list else None

def take_image(camera):
	print(f"Opening opencv camera using cam: {camera}...")

	try:
		cap	= cv2.VideoCapture(int(camera))
	except BrokenPipeError:
		logging.error("Client disconnected before response was fully sent.")

	while cap.isOpened(): 
		_, frame = cap.read()
		
		text		= "Hold 'Q' to Quit | Hold 'C' to Capture"
		font_family	= cv2.FONT_HERSHEY_SIMPLEX
		font_size	= 0.5
		font_weight	= 1
		text_color	= (255, 255, 255) 
		bg_color	= (0, 0, 0)

		# Get the text size
		(text_width, text_height), baseline = cv2.getTextSize(
			text 		= text, 
			fontFace	= font_family, 
			fontScale	= font_size, 
			thickness	= font_weight
		)

		# Set the position
		x = 10
		y = 30

		cv2.rectangle(
			img 		= frame, 
			pt1 		= (x, y - text_height - baseline), 
			pt2 		= (x + text_width, y + baseline), 
			color 		= bg_color, 
			thickness	= -1	# -1 fills the rectangle
		)  

		# Put the text over the background rectangle
		cv2.putText(
			img			= frame, 
			text		= text, 
			org			= (x, y), 
			fontFace	= font_family, 
			fontScale	= font_size, 
			color		= text_color, 
			thickness	= font_weight
		)
		
		# Show image back to screen
		cv2.imshow('OPERATE | Image Capture', frame)

		# exit
		if cv2.waitKey(10) & 0XFF == ord('q'):
			cap.release()
			cv2.destroyAllWindows()
			
			return False
		
		# capture
		if cv2.waitKey(10) & 0XFF == ord('c'):
			time		= timezone.now().strftime("%Y%m%d%H%M%S")
			image_path	= f"media/searches/{time}.jpg"
			
			cap.release()
			cv2.destroyAllWindows()
			
			return [image_path, frame]

def save_image(image_path, frame):
	return cv2.imwrite(image_path, frame)


def get_image_embedding(model_name, inp_image):
	session_options = ort.SessionOptions()
	session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
	session = ort.InferenceSession(str(Path().cwd().joinpath(f"facesearch/snn_models/{model_name}")))
	
	input_name	= session.get_inputs()[0].name
	output_name = session.get_outputs()[0].name

	return session.run([output_name], {input_name: inp_image})[0]


