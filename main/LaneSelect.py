'''
Created on Aug 11, 2018

@author: Babtu
'''
import numpy as np
import cv2
from scipy.spatial import distance as dist
import argparse
from classes.lane import Lane

def select_lanes(args):

	image = cv2.imread(args['path'])
	pts = []
	lanes = []
	mode = None

	def order(pts):
		pts = np.asarray(pts, dtype='int32')
		sort = sorted(pts, key=lambda k: k[1])
		diff = np.asarray([np.absolute([sort[i][1] - sort[i+1][1]])[0] for i in range(len(sort) - 1)])
		max_index = (diff.argmax(axis=0) + 1)
		top = sorted(sort[:max_index], key=lambda k: k[0])
		bottom = sorted(sort[max_index:], key=lambda k: k[0], reverse=True)
		sort = np.concatenate([top,bottom])
		return sort, max_index


	def mouse_select(event, x, y, flags, param):
		nonlocal image, lanes, mode, pts
		if mode is not None:
			if mode == 'select':
				if event == cv2.EVENT_LBUTTONDOWN:
					pts.append((x,y))
					cv2.circle(image,(x,y),7,(255,0,0),-1)
			elif mode == 'delete':
				lanes.pop()
				mode = None
				print('Lane Deleted!')
			else:
				if len(pts) > 0:
					pts, index = order(pts)
					lanes.append(Lane(pts, index, mode))
					print('Lane Added! ({})'.format(mode))
				pts = []



	cv2.namedWindow('Display')
	cv2.setMouseCallback('Display', mouse_select)

	print('Welcome to the lane selector! Here are the instructions:')
	print('In order to create a new lane, press the \'n\' key.')
	print('Then, click on whichever points enclose the lane.')
	print('After you have selected all of the points for one lane, \npress the \'d\' key.')
	print('You can repeat this process as many times as you want.\nOnce you are finished,',
	'press the \'f\' key to see all of your lanes and save the image.')

	while True:
		key = cv2.waitKey(1) & 0xFF
		if key == ord('n'):
			mode = 'select'
		elif key == ord('t'):
			mode = 'Through'
		elif key == ord('l'):
			mode = 'Left'
		elif key == ord('r'):
			mode = 'Right'
		elif key == ord('d'):
			mode = 'delete'
		elif key == ord('f'):
			lane_display = np.copy(image)
			for i,l in enumerate(lanes):
				colour = (255-i*20,255-i*10,i*5)
				cv2.drawContours(lane_display,[l.pts],-1,colour,-1)
				coords = (int(l.pts[l.index][0]-55),l.pts[-1][1]-10)
				colour = (i*20,i*10,255-i*5)
				cv2.putText(lane_display,str(i+1),coords,cv2.FONT_HERSHEY_COMPLEX,
							0.8,colour,2)
			cv2.imshow('Lanes',lane_display)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			if args.get('saved',False):
				save = input('Save image? (Say \'y\' for yes or \'n\' for no.) ')
				if save == 'y':
					cv2.imwrite(r'{}'.format(args['saved']),lane_display)
					print('Image written to {}.'.format(args['saved']))
				
			break
		cv2.imshow('Display',image)
	cv2.destroyAllWindows()
	print('{} lanes successfully added!'.format(len(lanes)))
	return lanes

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument('-p','--path',help='Path to the input image')
	ap.add_argument('-s','--saved',help='Path to where the saved image should go',
					required=False)
	args = vars(ap.parse_args())
	select_lanes(args)
