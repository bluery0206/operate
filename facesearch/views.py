from django.shortcuts import render
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

from .forms import UploadedImageForm
# from .operate_model import Preprocessing, DistanceLayer, FileHandler


cwd_path		= Path().cwd()

media_path		= cwd_path.joinpath("media")

database_path 	= media_path.joinpath("raw_image")
searches_path 	= media_path.joinpath("searches")

fs_path			= cwd_path.joinpath("facesearch")
models_path		= fs_path.joinpath("snn_models")

# prep	= Preprocessing()
# fh		= FileHandler()

def upload_image(request):
	context = {
		"form": form
	}

	if request.method == "POST":
		form = UploadedImageForm(request.POST, request.FILES)

		if form.is_valid():
			form.save()

			# # access image
			# request_img = request.FILES['image'].name
			# image_path 	= searches_path.joinpath(request_img)
			# image		= cv2.imread(str(image_path))

			# # Model instantiation
			# model_path	= str(models_path.joinpath("snn.h5"))
			# snn_model	= tf.keras.models.load_model(model_path, custom_objects={'DistanceLayer':DistanceLayer})
			# emb_gen		= snn_model.get_layer('EmbeddingGenerator')

			# # Achor embedding
			# anchor 		= prepare(image)
			# anchor_emb	= emb_gen.predict(anc, verbose=0)

			# # Database image paths
			# database_images = list(database_path.glob("*"))

			# threshold = 1

			# # Searching
			# best_candidate_dist, best_candidate_idx, candidates_list = search_face(database_images, anchor_emb, threshold)

			# context["best_candidate_dist"]	= best_candidate_dist
			# context["best_candidate_idx"]	= best_candidate_idx
			# context["candidates_list"]		= candidates_list

			# Delete the image
			image_path.unlink()
	else:
		form = UploadedImageForm()
	return render(request, "facesearch/upload_image.html", context)

# def prepare(image):
# 	image = prep.preprocess_image(image)
# 	image = prep.normalize_image(image)
# 	image = tf.expand_dims(image, axis=2)
# 	image = tf.expand_dims(image, axis=0)
# 	return image	

# def search_face(database_images, anchor_emb, threshold):
# 	# Best candidate initialization
# 	best_candidate_dist	= threshold
# 	best_candidate_idx	= False

# 	candidates_list	= []

# 	for idx, validation_image in enumerate(database_images):
# 		validation_image	= prepare(validation_image)
# 		validation_emb		= emb_gen.predict(anc, verbose=0)

# 		distance = np.linalg.norm(anchor_emb - validation_emb)

# 		if distance <= best_candidate_dist:
# 			best_candidate_dist	= distance
# 			best_candidate_idx	= idx

# 			candidates_list.append([best_candidate_dist, best_candidate_idx])

# 		if distance == 0:
# 			break

# 	return [best_candidate_dist, best_candidate_idx, candidates_list]