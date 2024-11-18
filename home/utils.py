from django.http import HttpResponse
from PIL import Image
from django.utils import timezone
import string
from docx.shared import Inches
from docx import Document
from pathlib import Path

cwd_path = Path().cwd()
media_path = cwd_path.joinpath("media")
outputs_path = media_path.joinpath("outputs")

def get_full_name(profile:object, m_initial:bool=True):
	full_name = profile.l_name

	if profile.f_name:
		full_name += f", {profile.f_name}"

	if profile.m_name and m_initial:
		full_name += f" {profile.m_name[0]}."
	elif profile.m_name:
		full_name += f" {profile.m_name}"

	if profile.suffix:
		full_name += f" {profile.suffix}"

	return full_name.title()

def format_text(text):
	symbols = string.punctuation.replace('_', ' ')
	translation_table = str.maketrans(symbols, '_' * len(symbols))

	text = text.replace(",", "")
	text = text.translate(translation_table)
	return text

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

def generate_docx(template_path, image_path, fields, data):
	doc = Document(template_path)

	# inserts the image
	for p in doc.paragraphs:
		if "raw_image" in p.text:
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
	save_path	= outputs_path.joinpath(file_name)
	doc.save(save_path)

	return [file_name, save_path]

def save_docx(file_name, save_path):
	with open(save_path, 'rb') as f:
		response = HttpResponse(
			f.read(),
			content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
		)
		response['Content-Disposition'] = f'attachment; filename="{file_name}"'
	
	save_path.unlink(save_path)

	return response