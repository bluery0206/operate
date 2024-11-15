import onnxruntime as ort
from pathlib import Path 
import numpy as np
import onnx
import cv2 
import random as rd

def crop_image_from_center(image):
    height, width = image.shape
    new_dimension = min(height, width)

    left    = int((width   - new_dimension) / 2)
    top     = int((height  - new_dimension) / 2)
    right   = int((width   + new_dimension) / 2)
    bottom  = int((height  + new_dimension) / 2)

    return image[top:bottom, left:right]
 
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

	return [best_cand_dist, best_cand_idx, cand_list] if best_cand_idx else None