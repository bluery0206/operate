from PIL import Image
from django.utils import timezone



def get_full_name(profile:object, m_initial:bool=True):
	full_name = profile.l_name

	if profile.f_name:
		full_name += f", {profile.f_name}"

	if profile.m_name:
		full_name += f" {profile.m_name}"
	elif profile.m_name and m_initial:
		full_name += f" {profile.m_name[0]}."

	if profile.suffix:
		full_name += f" {profile.suffix}"

	return full_name


def save_profile_picture(profile):	
	ori_img = Image.open(profile.raw_image.path)
	print(ori_img)
	width, height = ori_img.size

	# To set the height or width of the least size
	size 	= width if height > width else height

	# Finding the center
	left, top, right, bottom = get_img_size(width, height, size)

	new_img = ori_img.crop((left, top, right, bottom))
	new_img = new_img.resize((300, 300))

	# Just for name
	time 	= timezone.now().strftime("%Y%m%d%H%M%S")

	new_img_name = "thumbnails/" + time + ".png"
	ori_img_name = "raw_images/" + time + ".png"

	# Save images
	new_img.save("media/" + new_img_name)
	ori_img.save("media/" + ori_img_name)

	# Change image values
	profile.thumbnail 	= new_img_name
	profile.raw_image 	= ori_img_name

	res = profile.save()

def get_img_size(width, height, size) -> list:
	left 	= (width - size) / 2
	top 	= (height - size) / 2
	right 	= (width + size) / 2
	bottom 	= (height + size) / 2

	return [left, top, right, bottom]