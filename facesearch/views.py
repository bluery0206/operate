from django.shortcuts import render

from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

from .forms import UploadedImageForm
from .operate_model import Preprocessing

prep = Preprocessing()

cwd_path		= Path().cwd()
media_path		= cwd_path.joinpath("media")
database_path 	= media_path.joinpath("raw_image")
searches_path 	= media_path.joinpath("searches")
fs_path			= cwd_path.joinpath("facesearch")
models_path		= fs_path.joinpath("snn_models")

def upload_image(request):
	print(str(raw_image_path))

	if request.method == "POST":
		form = UploadedImageForm(request.POST, request.FILES)

		if form.is_valid():
			form.save()

			# access image
			request_img = request.FILES['image'].name
			image_path 	= searches_path.joinpath(request_img)
			image		= cv2.imread(str(image_path))

			# Search
			model_path	= str(models_path.joinpath("snn.h5"))
			model		= load_model(model_path)

			# Delete the image
			image_path.unlink()
	else:
		form = UploadedImageForm()
	return render(request, "facesearch/upload_image.html", {"form": form})



# def search(anchor):
# 	anc = prep.preprocess_image(anchor)

# 	anc = prep.normalize_image(anc)
# 	anc = tf.expand_dims(anc, axis=2)

# 	anc = tf.expand_dims(anc, axis=0)
# 	anc_emb = emb_gen.predict(anc, verbose=0)

# 	return [anc, anc_emb]

def load_model(model_path):
	snn = tf.keras.models.load_model(
		model_path,
		custom_objects = {
			'DistanceLayer' : DistanceLayer
		}
	)

	emb_gen = snn.get_layer('EmbeddingGenerator')