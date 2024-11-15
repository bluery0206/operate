from django.shortcuts import render
from pathlib import Path
from django.utils import timezone

from .forms import UploadedImageForm
from .utils import *

cwd_path		= Path().cwd()
media_path		= cwd_path.joinpath("media")
database_path 	= media_path.joinpath("raw_images")
searches_path 	= media_path.joinpath("searches")
fs_path			= cwd_path.joinpath("facesearch")
models_path		= fs_path.joinpath("snn_models")

def facesearch(request):
	context = {
		"form": UploadedImageForm()
	}

	if request.method == "POST":
		is_option_camera = request.POST.get("open_camera", 0)

		if is_option_camera:
			input_path = open_camera()
			input_name = format_image_name(input_path)
			input_path = Path(input_path)
		else:
			form = UploadedImageForm(request.POST, request.FILES)
			context['form'] = form

			if form.is_valid(): form.save()

			input_name = format_image_name(request.FILES['image'].name)
			input_path = Path().cwd().joinpath(f"media/searches/{input_name}")

		database_path	= Path().cwd().joinpath("media/raw_images")
		threshold		= 10

		cand_list = search(input_path, database_path, threshold)

		print(cand_list)

		if cand_list:
			profiles = get_profiles(cand_list, database_path)

			context["profiles"] = profiles

		# Delete the image
		input_path.unlink()

	return render(request, "facesearch/facesearch.html", context)

def open_camera():
	image_name = None
	camera = 0
	cap = cv2.VideoCapture(camera)

	while cap.isOpened(): 
		ret, frame = cap.read()
		
		# Cut down frame to 500x500px
		frame_size = 750
		frame = frame[120:120 + frame_size, 200:200 + frame_size, :] # np.ndarray
		
		# Show image back to screen
		cv2.imshow('Image Collection', frame)
		
		if cv2.waitKey(10) & 0XFF == ord(' '):
			time = timezone.now().strftime("%Y%m%d%H%M%S")
			image_name = f"media/searches/{time}.jpg"
			cv2.imwrite(image_name, frame)
			break
			
	cap.release()
	cv2.destroyAllWindows()
	
	return image_name