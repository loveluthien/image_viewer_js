import asyncio
import websockets
import json
import simplejson
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
import scipy as sp
import skimage


filename = input('Enter fits file:')

def json_serializer(obj):
	if isinstance(obj, np.ndarray):
		return obj.tolist()
	return obj

class init():
	def __init__(self):

		self.zoom_level = 1
		self.canvas00_size = [500, 400]
		

		# print(filename)
		# filename = '../alma_data/2015.1.00551/member.uid___A001_X2fa_X138.HLTau_HCOplus.fits'
		# filename = '../alma_data/2019.1.00847/member.uid___A001_X1467' +\
		# 	'_X264.04288p1802_sci.spw16.cube.I.pbcor.fits'
		# filename = '../alma_data/2015.1.00956/member.uid___A001_X2fb_X2af.n4303_CO21.pbcor.fits'
		fitsfile = fits.open(filename)
		self.header = fitsfile[0].header
		self.img_cube = fitsfile[0].data
		fitsfile.close()

		


		# self.fits_info()
		self.raw_img_size = self.img_cube[0,0,:,:].shape

		self.i_ch = 0
		self.cursor_x = 0
		self.cursor_y = 0
		self.raw_x_pix = 0
		self.raw_y_pix = 0
		# self.Intensity = 0


		self.default_img()
		self.update_img()
		self.update_img_range()

		
		self.hist_bin_num = 100
		self.update_hist()

		self.update_prof(axis='x')
		self.update_prof(axis='y')
		self.update_prof(axis='z')
		self.update_prof_range()



	def default_img(self):
		
		## determine the initial image size ##
		self.img_size = np.array(self.raw_img_size, dtype=int)
		
		## if the image size greater than the canvas size ## 
		dim = 2
		for i in range(dim):
			while self.img_size[i] > self.canvas00_size[i]:
				self.img_size = self.img_size / 2
				self.zoom_level = self.zoom_level / 2

		## if the image size smaller than the canvas size ## 
		while (self.canvas00_size[0]/self.img_size[0] > 2) & \
			(self.canvas00_size[1]/self.img_size[1] > 2):
			self.img_size = self.img_size * 2
			self.zoom_level = self.zoom_level * 2

		self.default_zoom_level = self.zoom_level
		self.fits_info()

		self.disp_raw_cen_pix = self.raw_cen_pix
		self.disp_cen_pix = self.cen_pix
		self.disp_center = self.center




	def fits_info(self):

		# self.zoom_level = 1

		hh = self.header
		self.wcs_info = WCS(naxis=3)
		self.wcs_info.wcs.crpix = [hh['CRPIX1']*self.zoom_level, 
									hh['CRPIX2']*self.zoom_level, 
									hh['CRPIX3']]
		self.wcs_info.wcs.crval = [hh['CRVAL1'], hh['CRVAL2'], hh['CRVAL3']]
		self.wcs_info.wcs.cunit = [hh['CUNIT1'], hh['CUNIT2'], hh['CUNIT3']]
		self.wcs_info.wcs.ctype = [hh['CTYPE1'], hh['CTYPE2'], hh['CTYPE3']]
		self.wcs_info.wcs.cdelt = [hh['CDELT1']/self.zoom_level, 
									hh['CDELT2']/self.zoom_level, 
									hh['CDELT3']]
		self.wcs_info.array_shape = [hh['NAXIS1']*self.zoom_level, 
										hh['NAXIS2']*self.zoom_level, 
										hh['NAXIS3']]
		
		self.img_xy = self.wcs_info.pixel_to_world_values(
							np.arange(self.wcs_info.array_shape[0]), 
							np.arange(self.wcs_info.array_shape[1]), 0)
		self.img_xy = np.array(self.img_xy)
		img_z = self.wcs_info.pixel_to_world_values(0, 0, np.arange(hh['NAXIS3']))
		img_z = np.array(img_z)/1e9 # Hz to GHz

		self.img_x = self.img_xy[0, :]
		self.img_y = self.img_xy[1, :]
		self.img_z = img_z[2,:]

		prof_pix_fac = max(1, self.zoom_level)
		self.x_pix_list = np.arange(hh['NAXIS1']*prof_pix_fac)
		self.y_pix_list = np.arange(hh['NAXIS2']*prof_pix_fac)

		self.raw_cen_pix = [int(self.header['NAXIS1']/2), 
							int(self.header['NAXIS2']/2)]
		

		self.cen_pix = [int(self.raw_cen_pix[0]*self.zoom_level), 
							int(self.raw_cen_pix[1]*self.zoom_level)]
		# print(self.zoom_level, self.raw_cen_pix, self.cen_pix)

		self.center = [self.img_x[self.cen_pix[0]], 
						self.img_y[self.cen_pix[1]]]


	def update_img(self):
		self.img = self.img_cube[0,self.i_ch,:,:]
		self.resize_img()
		self.clip_img()


	def resize_img(self):

		down_factor = int(1 / self.zoom_level)
		
		## if the image size greater than the canvas size, downsampling the image 
		if down_factor > 1:
			self.img = skimage.measure.block_reduce(self.img, 
								(down_factor, down_factor), np.nanmean)
		
		elif down_factor < 1:
			self.img = sp.ndimage.zoom(self.img, self.zoom_level, order=0)
		
		self.img_size = self.img.shape


	def clip_img(self):

		if (self.img_size[0] > self.canvas00_size[0]) \
			| (self.img_size[1] > self.canvas00_size[1]):

			x_bound = [max(int(self.disp_cen_pix[0] - self.canvas00_size[0]/2), 0),
						min(int(self.disp_cen_pix[0] + self.canvas00_size[0]/2), 
							self.img_size[0])]
			y_bound = [max(int(self.disp_cen_pix[1] - self.canvas00_size[1]/2), 0),
						min(int(self.disp_cen_pix[1] + self.canvas00_size[1]/2), 
							self.img_size[1])]

			# print('xbound', x_bound)
			# print('cen pix1', self.disp_cen_pix)
			# print('img size', self.img_size)
			self.img = self.img[y_bound[0]: y_bound[1], x_bound[0]: x_bound[1]]

			self.img_x = self.img_x[x_bound[0]: x_bound[1]]
			self.img_y = self.img_y[y_bound[0]: y_bound[1]]



	def update_img_range(self):

		x_range_half = self.canvas00_size[0]*self.wcs_info.wcs.cdelt[0]/2
		y_range_half = self.canvas00_size[1]*self.wcs_info.wcs.cdelt[1]/2

		self.img_x_range = [self.disp_center[0] - x_range_half, 
							self.disp_center[0] + x_range_half]
		self.img_y_range = [self.disp_center[1] - y_range_half, 
							self.disp_center[1] + y_range_half]
		


	def update_hist(self):
		ch_slice = self.img_cube[0,self.i_ch,:,:].flat[:]
		bins = np.linspace(np.nanmin(ch_slice), np.nanmax(ch_slice), self.hist_bin_num+1)
		self.hist_data, temp = np.histogram(ch_slice, bins=bins)
		self.hist_x = (bins[1:] + bins[:-1])/2

		self.data_percent = 99 # %
		self.vmax = np.nanpercentile(ch_slice.flat[:], 
										50 + self.data_percent/2 )
		self.vmin = np.nanpercentile(ch_slice.flat[:], 
										50 - self.data_percent/2 )
		self.count_max = np.nanmax(self.hist_data) * 1.1
		


	def update_cursor_pix(self):

		xx = np.where(self.img_size[0] < self.canvas00_size[0],
					self.img_size[0]/2, self.canvas00_size[0]/2)
		yy = np.where(self.img_size[1] < self.canvas00_size[1], 
					self.img_size[1]/2, self.canvas00_size[1]/2)

		self.x_pix = int((self.cen_pix[0] - xx + self.cursor_x))
		self.y_pix = int((self.cen_pix[1] - yy + self.cursor_y))

		self.raw_x_pix = int(self.x_pix/self.zoom_level - 1)
		self.raw_y_pix = int(self.y_pix/self.zoom_level)
		# print(self.zoom_level, self.raw_x_pix, self.raw_y_pix)



	def update_disp_center(self):

		self.disp_raw_cen_pix = [self.raw_x_pix, self.raw_y_pix]


	def update_cen_pix(self):

		self.disp_cen_pix = [int(self.disp_raw_cen_pix[0]*self.zoom_level), 
							int(self.disp_raw_cen_pix[1]*self.zoom_level)]

		self.disp_center = [self.img_x[self.disp_cen_pix[0]], 
						self.img_y[self.disp_cen_pix[1]]]
		

	def update_prof(self, axis='x'):
		
		if (self.raw_x_pix < self.raw_img_size[0]) \
			& (self.raw_y_pix < self.raw_img_size[1]):

			if axis == 'x':
				self.prof_x = self.img_cube[0, self.i_ch, self.raw_y_pix, :]

			if axis == 'y':
				self.prof_y = self.img_cube[0, self.i_ch, :, self.raw_x_pix]

			if axis == 'z':
				self.prof_z = self.img_cube[0,:, self.raw_y_pix, self.raw_x_pix]



	def update_prof_range(self):
		
		prof_pix_fac = max(1, self.zoom_level)
		xx = np.where(self.img_size[0] < self.canvas00_size[0],
					self.raw_img_size[0]/2, self.canvas00_size[0]/2)
		yy = np.where(self.img_size[1] < self.canvas00_size[1], 
					self.raw_img_size[1]/2, self.canvas00_size[1]/2)
		
		xx_bound = [max((self.disp_cen_pix[0] - xx)/prof_pix_fac, 0),
					min((self.disp_cen_pix[0] + xx)/prof_pix_fac, 
		self.raw_img_size[0])]

		yy_bound = [max((self.disp_cen_pix[1] - yy)/prof_pix_fac, 0),
					min((self.disp_cen_pix[1] + yy)/prof_pix_fac, 
		self.raw_img_size[1])]

		self.prof_x_range = [xx_bound[0], xx_bound[1]]
		self.prof_y_range = [yy_bound[0], yy_bound[1]]



def create_message(App, panels):

	message_dict = {
		'img': {'data': App.img, 
				'x': App.img_x, 
				'y': App.img_y,
				'x_range': App.img_x_range,
				'y_range': App.img_y_range,
				'vmax': App.vmax,
				'vmin': App.vmin,},
		'hist': {'data': App.hist_data,
				'x': App.hist_x,
				'vmax': App.vmax,
				'vmin': App.vmin,
				'count_max': App.count_max,},
		'prof_x': {'data': App.prof_x,
				'x': App.x_pix_list, 
				'x_range': App.prof_x_range},
		'prof_y': {'data': App.prof_y,
				'x': App.y_pix_list, 
				'x_range': App.prof_y_range},			
		'prof_z': {'data': App.prof_z,
				'x': App.img_z,},
			}

	message_send = {'data_size': App.wcs_info.array_shape,
					'zoom_level': App.zoom_level,
					'cen_pix': App.cen_pix, 
					'raw_xpix': App.raw_x_pix,
					'raw_ypix': App.raw_y_pix,
	}

	for field in panels:
		message_send[field] = message_dict[field]

	# message = json.dumps(message_send, default=json_serializer)
	message = simplejson.dumps(message_send, default=json_serializer, 
				ignore_nan=True)

	return message



## websocket data transfer ##
async def handler(websocket):

	App = init()

	while True:	

		try:

			message_in = await websocket.recv()
			message_in_dict = json.loads(message_in)

			if message_in_dict['greeting'] == 'Hello kitty?':
				print('Ahoy')
				panels = ['img', 'hist', 'prof_x', 'prof_y', 'prof_z']
				message_out = create_message(App, panels)
				await websocket.send(message_out)

			updates = message_in_dict['updates']

			for update in updates:
				if update == 'i_ch':
					App.i_ch = int(message_in_dict['i_ch'])
					App.fits_info()
					App.update_img()
					App.update_hist()
					App.update_prof(axis='x')
					App.update_prof(axis='y')
					App.update_prof_range()
					panels = ['img', 'hist', 'prof_x', 'prof_y']
					message_out = create_message(App, panels)
					await websocket.send(message_out)

				if update == 'cursor':
					App.cursor_x = int(message_in_dict['cursor_x'])
					App.cursor_y = int(message_in_dict['cursor_y'])
					App.update_cursor_pix()
					App.update_prof(axis='x')
					App.update_prof(axis='y')
					App.update_prof(axis='z')
					App.update_prof_range()
					message_out = create_message(App, ['prof_x', 'prof_y', 'prof_z'])
					await websocket.send(message_out)


				if update == 'zoom_level':
					App.zoom_level = message_in_dict['zoom_level']
					App.fits_info()
					App.update_cen_pix()
					App.update_img()
					App.update_img_range()
					App.update_prof_range()
					message_out = create_message(App, ['img', 'prof_x', 'prof_z'])
					await websocket.send(message_out)


				if update == 'center':
					if 	(App.disp_raw_cen_pix[0] != App.raw_x_pix) \
						| (App.disp_raw_cen_pix[1] != App.raw_y_pix):
						App.fits_info()
						App.update_disp_center()
						App.update_cen_pix()
						App.update_img()
						App.update_img_range()
						App.update_prof_range()
						message_out = create_message(App, ['img', 'prof_x', 'prof_y'])
						await websocket.send(message_out)


		except websockets.ConnectionClosedOK:
			break
		


async def main():

	async with websockets.serve(handler, "localhost", 9107):
		await asyncio.Future()  # run forever


if __name__ == "__main__":
	asyncio.run(main())
