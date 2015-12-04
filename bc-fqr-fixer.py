#!/usr/bin/python2.7
import PIL
import sys
import os

args = sys.argv[1:]

def print_help():
	print "Usage:", sys.argv[0], "broken.fqr[Broken QR array file]"
	print "      ", sys.argv[0], "--gen-qr N [filename]  -- Generate empty qr of size NxN if"
	print "                                              filename is given write to file"
	print """
array file format:

*...xxx***x*x**x
xx****xxxx*..***

'x' or 'X' => black
'o' => white
'.' => unknown

It should be an NxN matrix with only 'x', '.' and '*' characters

NOTE: Spaces and empty lines will be removed
"""
	sys.exit(-1)

len_args = len(args)

if len_args is 0:
	print_help()

if args[0] == "--gen-qr":
	if len_args < 2:
		print "Missing N\n"
		print_help()
	try:
		N = int(args[1])
	except:
		print "N should be integer but given: ", args[1], "\n"
		print_help()

	qr = [['.' for col in range(N)] for row in range(N)]
	qr_str = '\n'.join([''.join(s) for s in qr])+'\n'
	if len_args > 2:
		with open(args[2], 'w') as f:
			f.write(qr_str)
	else:
		print qr_str
	sys.exit(0)

class MalformedFQRException(Exception):

	def __init__(self, msg):
		super(MalformedFQRException, msg)


class FQR(object):

	POS_CORNER_STR = [
"xxxxxxx",
"x     x",
"x xxx x",
"x xxx x",
"x xxx x",
"x     x",
"xxxxxxx"
]
	POS_CORNER_AR = []

	FORMATS = [
	('L', 0, "xxx xxxxx   x  "),
	('L', 1, "xxx  x xxxx  xx"),
	('L', 2, "xxxxx xx x x x "),
	('L', 3, "xxxx   x  xxx x"),
	('L', 4, "xx  xx   x xxxx"),
	('L', 5, "xx   xx   xx   "),
	('L', 6, "xx xx   x     x"),
	('L', 7, "xx x  x xxx xx "),
	('M', 0, "x x x     x  x "),
	('M', 1, "x x   x  x  x x"),
	('M', 2, "x xxxx  xxxxx  "),
	('M', 3, "x xx xx x  x xx"),
	('M', 4, "x   x xxxxxx  x"),
	('M', 5, "x      xx  xxx "),
	('M', 6, "x  xxxxx  x xxx"),
	('M', 7, "x  x x x x     "),
	('Q', 0, " xx x x x xxxxx"),
	('Q', 1, " xx     xx x   "),
	('Q', 2, " xxxxxx  xx   x"),
	('Q', 3, " xxx x      xx "),
	('Q', 4, " x  x  x xx x  "),
	('Q', 5, " x    xx     xx"),
	('Q', 6, " x xxx xx xx x "),
	('Q', 7, " x x xxxxx xx x"),
	('H', 0, "  x xx x   x  x"),
	('H', 1, "  x  xxx xxxxx "),
	('H', 2, "  xxx  xxx  xxx"),
	('H', 3, "  xx  xxx x    "),
	('H', 4, "    xxx xx   x "),
	('H', 5, "     x  x x x x"),
	('H', 6, "   xx x    xx  "),
	('H', 7, "   x     xxx xx")
]
	def __init__(self, path=None):
		self.dirty = False
		self.N = -1
		self.qr_str = []
		self.qr_ar = []
		self.pos_corner = [] # 0: LT, 1: RT, 2: LB, 3: LT
		self.pos_inner = [] # 0,1,... depends on version
		if path is not None:
			self.load_qr(path)

# ASSUMES GIVEN STR LIST IS NxN
	@staticmethod
	def qr_str2ar(qr_str):
		N = len(qr_str)
		qr_ar = [ [-1 for i in range(N)] for j in range(N)]
		for i in range(N):
			for j in range(N):
				c = qr_str[i][j]
				if c == 'x':
					qr_ar[i][j] = 1
				elif c == 'o':
					qr_ar[i][j] = 0
		return qr_ar

# ASSUMES GIVEN STR LIST IS NxN
	@staticmethod
	def qr_ar2str(qr_ar):
		N = len(qr_ar)
		qr_str = [ ['.' for i in range(N)] for j in range(N)]
		for i in range(N):
			for j in range(N):
				c = qr_ar[i][j]
				if c == 1:
					qr_str[i][j] = 'x'
				elif c == 0:
					qr_str[i][j] = 'o'
		return [''.join(x) for x in qr_str]

# ASSUMES GIVEN STR LIST IS NxN
	@staticmethod
	def print_qr_ar(qr_ar):
		print '\n'.join(FQR.qr_ar2str(qr_ar))

	def load_qr(self, path):
		self.dirty = True
		with open(path, 'r') as f:
			# read non empty lines after erasing spaces and EOLs
			self.qr_str = [x.strip().lower() for x in f.readlines() if len(x)>1]
			self.N = len(self.qr_str)
			error = ""
			for line in self.qr_str:
				print line
				if len(line) != self.N:
					error = "Dimensions does not match: line_len, N: "+str(len(line))+", "+str(self.N)
				elif any(ch not in 'x .' for ch in line):
					error = "Unwanted character on last line"
				if error != "":
					raise MalformedFQRException(error)

			self.dirty = False
			print "\nLoaded successfully:", path, "\n"
		if self.dirty:
			if not os.path.exists(args[0]):
				print "File could not be found: ", ' '.join(args)
				sys.exit(-1)
			print "QR read error"
		self.qr_ar = FQR.qr_str2ar(self.qr_str)

	def find_positionings(self):
		s_qr = [ s[0:7] for s in self.qr_ar[0:7] ]
		if FQR.POS_CORNER_AR == s_qr:
			print "Position found: LT"
			for i in range(8):
				self.qr_ar[0][i] = 0
				self.qr_ar[i][0] = 0

		s_qr = [ s[-7:] for s in self.qr_ar[0:7] ]
		if FQR.POS_CORNER_AR == s_qr:
			print "Position found: RT"
			for i in range(8):
				self.qr_ar[7][self.N-i-1] = 0
				self.qr_ar[i][self.N-8] = 0
			self.pos_corner.append(1)

		FQR.print_qr_ar(self.qr_ar)

FQR.POS_CORNER_AR = FQR.qr_str2ar(FQR.POS_CORNER_STR)

fqr = FQR()
fqr.load_qr(args[0])

fqr.find_positionings()
