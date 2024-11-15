from django.shortcuts import render
from pathlib import Path
import cv2

from .forms import UploadedImageForm
from .operate_model import *
from profiles.models import Personnel, Inmate
from django.utils import timezone

cwd_path		= Path().cwd()
media_path		= cwd_path.joinpath("media")
database_path 	= media_path.joinpath("raw_images")
searches_path 	= media_path.joinpath("searches")
fs_path			= cwd_path.joinpath("facesearch")
models_path		= fs_path.joinpath("snn_models")

def upload_image(request):
	context = {}

	if request.method == "POST":
		form = UploadedImageForm(request.POST, request.FILES)

		if form.is_valid():
			form.save()

			# access image
			request_img_name = request.FILES['image'].name

			# replaces any spaces with _ in image name
			# can cause errors in for later accessing
			request_img_name = request_img_name.replace(" ", "_") if " " in request_img_name else request_img_name

			# fetching and preprocessing dataset/validation images
			inp_image_p	= searches_path.joinpath(request_img_name)
			inp_image	= open_gray_image(str(inp_image_p))
			inp_image	= preprocess_image(inp_image)

			# fetching and preprocessing dataset/validation images
			val_image_p = list(database_path.glob("*"))
			val_images	= [open_gray_image(str(val_image)) for val_image in val_image_p]
			val_images	= [preprocess_image(val_image) for val_image in val_images]

			result = search_face(
				inp_image	= inp_image, 
				val_images	= val_images, 
				threshold	= 5
			)

			# getting profile objects of fetched images if any
			if result:
				cands = []
				_, _, cand_list = result

				# convert all dist to be float
				dists = [float(dist) for dist, idx in cand_list]

				# fetching images in result
				images = [str(val_image_p[idx]) for dist, idx in cand_list]
				
				for image in images:

					# getting image name from full path
					image_name = image.split("\\")[-1]

					personnel	= Personnel.objects.filter(raw_image__endswith=image_name).first()
					inmate		= Inmate.objects.filter(raw_image__endswith=image_name).first()

					# if personnel is not found then the image must be from inmate
					profile = personnel if personnel else inmate

					if profile: cands.append(profile)

				result = list(zip(dists, cands))
				result = sorted(result, reverse=False)

				context["result"] = result

			# Delete the image
			inp_image_p.unlink()
	else:
		form = UploadedImageForm()

	context["form"] = form

	return render(request, "facesearch/upload_image.html", context)

def open_camera(request):
	# cap = cv2.VideoCapture(0)
	# while cap.isOpened(): 
	# 	ret, frame = cap.read()
	
	# 	# Cut down frame to 500x500px
	# 	frame_size = 500
	# 	frame = frame[120:120 + frame_size, 200:200 + frame_size, :]
		
	# 	if cv2.waitKey(1) & 0XFF == ord('a'):
	# 		time = timezone.now().strftime("%Y%m%d%H%M%S")
	# 		cv2.imwrite(f"media/searches/{time}.jpg")
		
	# 	# Show image back to screen
	# 	cv2.imshow('Image Collection', frame)
		
	# 	# Breaking gracefully
	# 	if cv2.waitKey(1) & 0XFF == ord('q'):
	# 		break
			
	# cap.release()
	# cv2.destroyAllWindows()
	# return render(request, "facesearch/upload_image.html")

	# from PIL import Image
	# from django.utils import timezone

	# def save_profile_picture(profile):	
	# 	ori_img = Image.open(profile.raw_image.path)
	# 	print(ori_img)
	# 	width, height = ori_img.size

	# 	# To set the height or width of the least size
	# 	size 	= width if height > width else height

	# 	# Finding the center
	# 	left, top, right, bottom = get_img_size(width, height, size)

	# 	new_img = ori_img.crop((left, top, right, bottom))
	# 	new_img = new_img.resize((300, 300))

	# 	# Just for name
	# 	time 	= timezone.now().strftime("%Y%m%d%H%M%S")

	# 	new_img_name = "thumbnails/" + time + ".png"
	# 	ori_img_name = "raw_images/" + time + ".png"

	# 	# Save images
	# 	new_img.save("media/" + new_img_name)
	# 	ori_img.save("media/" + ori_img_name)

	# 	# Change image values
	# 	profile.thumbnail 	= new_img_name
	# 	profile.raw_image 	= ori_img_name

	# 	res = profile.save()

	# def get_img_size(width, height, size) -> list:
	# 	left 	= (width - size) / 2
	# 	top 	= (height - size) / 2
	# 	right 	= (width + size) / 2
	# 	bottom 	= (height + size) / 2

	# 	return [left, top, right, bottom]

	pass 