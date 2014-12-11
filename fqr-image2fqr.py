#!/usr/bin/python2.7
from PIL import Image
import sys
import os
import numpy

args = sys.argv[1:]

def print_help():
	print "Usage:", sys.argv[0], "input-file qr-dimension [output-file]  image input to fqr output"
	sys.exit(-1)

len_args = len(args)

if len_args is 0:
	print_help()

if not os.path.exists(args[0]) or args[0][-3:] not in ('png', 'jpg', 'bmp'):
	print "File could not be found: ", ' '.join(args)
	sys.exit(-1)

N = int(args[1])

# read as RGB to erase alpha
img = Image.open(args[0]).convert('RGB')
w, h = img.size
pix = h/N

first = True
qr = [['.' for i in range(N+1)] for j in range(N)]
for i in range(N):
	for j in range(N):
		sub_img = img.crop((j*pix, i*pix, (j+1)*pix, (i+1)*pix))
		img_ar = numpy.array(sub_img, dtype=numpy.float)
		avg = numpy.average(img_ar)
		if avg < 10:
			qr[i][j] = 'X'
		if avg > 246:
			qr[i][j] = ' '
		if i==7 or i==N-8 or j==7 or j==N-8:
			qr[i][j] = '.'
	qr[i][N] = '|'

qr_str = '\n'.join([''.join(s) for s in qr])+'\n'
if len_args > 2:
	with open(args[2], 'w') as f:
		f.write(qr_str)
else:
	print qr_str
