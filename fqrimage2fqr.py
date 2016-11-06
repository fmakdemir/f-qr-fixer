#!/usr/bin/env python3.5
from PIL import Image
import sys
import os
import numpy as np
from qrtools import QR
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', help='QR image file without margin')
parser.add_argument('qrsize', action='store', type=int, help='Size of QR in the image file')
parser.add_argument('-o', '--out-name', action='store', help='Output name for generated Fqr text file and cleaned image')
args = parser.parse_args()

def print_help():
	parser.print_help()
	print("Usage:", sys.argv[0], "input-file qr-dimension [fqr-name]")
	print("nimage input to fqr output\nImage must not have margin")
	sys.exit(-1)

if len(sys.argv) == 1:
	print_help()

if not os.path.exists(args.file):
	print("File could not be found: ", ' '.join(args))
	sys.exit(-1)

if args.file[-3:] not in ('png', 'jpg', 'bmp'):
	print("File format should be one of: png, jpg, bmp")
	sys.exit(-1)

def save_qr_img(qr, path=None):
	dqr = np.array(qr) # copy
	dqr[dqr == 'X'] = '0' # turn str array to color array
	dqr[dqr == '.'] = '1'
	dqr[dqr == '*'] = '2'
	dqr = dqr.astype(np.uint8)
	dqr[dqr == 0] = 0 # turn str array to color array
	dqr[dqr == 1] = 255
	dqr[dqr == 2] = 128
	N = len(dqr)
	nqr = np.zeros((N*8, N*8)) # x8 zoom image
	for i in range(N*8):
		for j in range(N*8):
			nqr[i, j] = dqr[i//8, j//8]
			if nqr[i, j] == 128:
				nqr[i, j] = ((i+j)%2)*255
	img = Image.fromarray(np.uint8(nqr))
	if path is None:
		img.show()
	else:
		img.save(path)

N = args.qrsize

# read as RGB to erase alpha
img = Image.open(args.file).convert('RGB')
w, h = img.size
pix = float(h)/N

qr = [['*' for i in range(N)] for j in range(N)]
for i in range(N):
	for j in range(N):
		box = (int(j*pix), int(i*pix), int((j+1)*pix), int((i+1)*pix))
		sub_img = img.crop(box)
		img_ar = np.array(sub_img, dtype=np.float)
		avg = np.median(img_ar)
		if avg < 120:
			qr[i][j] = 'X'
		if avg > 180:
			qr[i][j] = '.'

qr_str = '\n'.join([''.join(s) for s in qr])+'\n'
if args.out_name is not None:
	with open(args.out_name+'.fqr', 'w') as f:
		f.write(qr_str)
	img_path = args.out_name+'-clean.png'
	save_qr_img(qr, img_path)
	myCode = QR(filename=img_path)
	if myCode.decode():
		print('data type:', myCode.data_type)
		print('raw data:', myCode.data)
		print('string data:', myCode.data_to_string())
else:
	print(qr_str)
	save_qr_img(qr)

