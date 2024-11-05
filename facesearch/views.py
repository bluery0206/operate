from django.shortcuts import render

from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

from .forms import UploadedImageForm
from .operate_model import Preprocessing

prep = Preprocessing()

cwd				= Path().cwd()
media_path		= cwd.joinpath("media")

raw_image_path 	= media_path.joinpath("raw_image")
searches_path 	= media_path.joinpath("searches")

def upload_image(request):
	print(str(raw_image_path))

	if request.method == "POST":
		form = UploadedImageForm(request.POST, request.FILES)

		if form.is_valid():
			# uploaded_image.name: Name of the file.
			# uploaded_image.size: File size.
			# uploaded_image.content_type

			form.save()

			image 		= request.FILES['image'].name
			image_path 	= searches_path.joinpath(image)
			print("\n\nnew matadafaka:", image_path)

			opened_img 	= cv2.imread(str(image_path))
			img = cv2.resize(opened_img, (400, 400))

			# # just to fucking preview the image.
			# cv2.imshow("udk",img)
			# cv2.waitKey(0)  # Wait for a key press to close the window
			# cv2.destroyAllWindows()
			# print("\n\nnew matadafaka:", opened_img)

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

# def load_model(model_path):
# 	snn = tf.keras.models.load_model(
# 		model_path,
# 		custom_objects = {
# 			'DistanceLayer' : DistanceLayer
# 		}
# 	)

# 	emb_gen = snn.get_layer('EmbeddingGenerator')