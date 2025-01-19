import numpy as np
import cv2
import logging

from .excepts import *

logger = logging.getLogger(__name__)

class Camera:
	def __init__(
			self, 
			cam_id		:int, 
			cam_clipping:bool, 
			clip_size	:int, 
			detect_live	:bool 	= False, 
			show_bbox	:bool 	= False,
			wnd_title	:str 	= "OPerate | c: capture, q:exit",
		):
		self.cam_id 		= cam_id
		self.cam_clipping	= cam_clipping
		self.clip_size 		= clip_size
		self.detect_live	= detect_live
		self.show_bbox 		= show_bbox
		self.wnd_title		= wnd_title

		self.cap = cv2.VideoCapture(self.cam_id)
	
	def get_clip_corner_coords(self):
		cam_width 	= int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		cam_height 	= int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

		# w = 640, h = 480
		x = int((cam_height / 2) - (self.clip_size / 2))
		y = int((cam_width / 2) - (self.clip_size / 2))

		return [x, y]
	
	def clip_frame(self, frame:np.ndarray) -> np.ndarray:
		x, y = self.get_clip_corner_coords()

		top 	= x
		bot 	= x + self.clip_size
		left 	= y
		right 	= y + self.clip_size

		return frame[top:bot, left:right, :]
	
	def close_camera(self):
		self.cap.release()
		cv2.destroyAllWindows()

	def live_feed(self):
		# Showing a dummy first so that the while loop below will only break when needed.
		# This also enables the closing of the cam window through the `X` button which was 
		# 	before not doable and had to hold `q` from the keyboard to close it.
		# The `cv2.getWindowProperty()` returns `0.0` if the X button is pressed and `1.0`
		# 	otherwise.
		# By setting the cam window property to 1 by showing something (in this case, the 
		# 	dummy image), the condition below will be False and will not break and only if 
		# 	we pressed the X button or `q` from the keyboard.
		dummy_img = np.array([0.0, 0.0, 0.0])
		cv2.imshow(self.wnd_title, dummy_img)

		output 		= None
		has_output 	= False

		while cv2.getWindowProperty(self.wnd_title, cv2.WND_PROP_VISIBLE) > 0.0: 
			_, frame = self.cap.read()
			
			# Reduce camera window size
			if self.cam_clipping: frame = self.clip_frame(frame)

			# Display frame
			cv2.imshow(self.wnd_title, frame)

			if (cv2.waitKey(1) & 0XFF == ord('q')):
				break

			# Capture
			if (cv2.waitKey(1) & 0XFF == ord('c')):
				output 		= frame
				has_output 	= True
				self.close_camera()
				return [has_output, output]

		exception_message = "Closing Camera..."
		logger.exception(exception_message)
		self.close_camera()
		raise CameraShutdownException(exception_message)
