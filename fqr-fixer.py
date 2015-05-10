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

.   xxx...x.x..x
xx....xxxx.  ...

'x' or 'X' => black
' ' => white
'.' => unknown
'|' => line ending because if there is space at the end my sublime erase it

It should be an NxN matrix with only 'x', '.' and ' ' characters

NOTE: Don't use space at the end of lines
"""
# '.' is unknown because it is also regexp wildcard
# ' ' is white because it is space
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



class FQR(object):

	POS_CORNER = [ list(x) for x in [
		"xxxxxxx",
		"x     x",
		"x xxx x",
		"x xxx x",
		"x xxx x",
		"x     x",
		"xxxxxxx"
		] ]

	BLACK = ord('x')
	WHITE = ord(' ')
	UNKNW = ord('.')

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
		self.dirty = True
		self.N = -1
		self.qr = []
		# corner position
		self.pos_corner = [] # 0: LT, 1: RT, 2: LB, 3: LT
		# align position
		self.pos_align = [] # 0,1,... depends on version
		if path is not None:
			self.load_qr(path)

	@staticmethod
	def print_qr(qr):
		print '\n'.join([ ''.join(x) for x in qr])

	def load_qr(self, path):
		self.dirty = True
		with open(path, 'r') as f:
			# read non empty lines, erase end of lines
			self.qr = [ list( x.strip('|\n').lower() ) for x in f.readlines() if len(x)>1]
			self.N = len(self.qr)
			error = ""
			for line in self.qr:
				print ''.join(line)
				if len(line) != self.N:
					error = "Dimensions does not match: line_len, N: "+str(len(line))+", "+str(self.N)
				elif any(ch not in 'x .' for ch in line):
					error = "Unwanted character on last line"
				if error != "":
					print "Loaded FQR array is not in right format:\n\tError: ", error
					return

			self.dirty = False
			print "\nLoaded successfully:", path, "\n"
		if self.dirty:
			if not os.path.exists(args[0]):
				print "File could not be found: ", ' '.join(args)
				sys.exit(-1)
			print "QR read error"

	def find_positionings(self):
		s_qr = [ s[0:7] for s in self.qr[0:7] ]
		if FQR.POS_CORNER == s_qr:
			print "Position found: LT"
			for i in range(8):
				self.qr[7][i] = ' '
				self.qr[i][7] = ' '
			self.pos_corner.append(0)

		s_qr = [ s[-7:] for s in self.qr[:7] ]
		if FQR.POS_CORNER == s_qr:
			print "Position found: RT"
			for i in range(8):
				self.qr[7][-i-1] = ' '
				self.qr[i][  -8] = ' '
			self.pos_corner.append(1)

		s_qr = [ s[:7] for s in self.qr[:7] ]
		if FQR.POS_CORNER == s_qr:
			print "Position found: LB"
			for i in range(8):
				self.qr[-i-1][7] = ' '
				self.qr[-8][i] = ' '
			self.pos_corner.append(2)

		s_qr = [ s[-7:] for s in self.qr[-7:] ]
		if FQR.POS_CORNER == s_qr:
			print "Position found: RB"
			for i in range(8):
				self.qr[-8][-i-1] = ' '
				self.qr[-i-1][-8] = ' '
			self.pos_corner.append(3)


		FQR.print_qr(self.qr)

fqr = FQR()
fqr.load_qr(args[0])

fqr.find_positionings()


"""
* detect qr size
* orientation detection
* possible orientation list for fix algorithms
* for each possible fqr matrix we will try to fix it by
** fixing corners
** trying possible masks
** trying possible missing bits
** give possible results (with filters such as visible ascii)
"""
