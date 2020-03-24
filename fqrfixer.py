#!/usr/bin/env python3
#from __future__ import division
import PIL
import sys
import os
import argparse
import numpy as np

def print_fqr_format():
	print('''fqr file format:

*...xxx***x*x**x
xx****xxxx*..***

'x' or 'X' => black
'.' => white
'*' => unknown

It should be an NxN matrix with only 'x', '.' and '*' characters

Spaces around lines will be erased and empty lines will be ignored

Size must be NxN where N is (4*qr_version+17) meaning 21, 25, 29..., 177
1<=qr_version<=40
''')

class MalformedFQRException(Exception):

	def __init__(self, msg):
		super(MalformedFQRException, self).__init__(msg)

# calculate mask val at pos i, j with mask k
def get_mask(k):
    if k == 0:
        return lambda i, j: (i + j) % 2 == 0
    if k == 1:
        return lambda i, j: i % 2 == 0
    if k == 2:
        return lambda i, j: j % 3 == 0
    if k == 3:
        return lambda i, j: (i + j) % 3 == 0
    if k == 4:
        return lambda i, j: (i // 2 + j // 3) % 2 == 0
    if k == 5:
        return lambda i, j: (i * j) % 2 + (i * j) % 3 == 0
    if k == 6:
        return lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0
    if k == 7:
        return lambda i, j: ((i * j) % 3 + (i + j) % 2) % 2 == 0

def bin_ar_to_int(bin_ar):
	bs = ''.join(bin_ar).replace('x', '1').replace('.', '0')
	return int(bs, 2)

class FQR(object):

	FINDER_POS = ['LT', 'RT', 'LB', 'LT']

	FINDER_POS_PATTERN = np.array([ list(x) for x in [
		'xxxxxxx',
		'x.....x',
		'x.xxx.x',
		'x.xxx.x',
		'x.xxx.x',
		'x.....x',
		'xxxxxxx'
		]
	])

	ALIGN_PATTERN =  np.array([ list(x) for x in [
		'xxxxx',
		'x...x',
		'x.x.x',
		'x...x',
		'xxxxx'
		]
	])

	# version, location list
	ALIGN_PATTERN_LOC = [
		(2, [6, 18]),
		(3, [6, 22]),
		(4, [6, 26]),
		(5, [6, 30]),
		(6, [6, 34]),
		(7, [6, 22, 38]),
		(8, [6, 24, 42]),
		(9, [6, 26, 46]),
		(10, [6, 28, 50]),
		(11, [6, 30, 54]),
		(12, [6, 32, 58]),
		(13, [6, 34, 62]),
		(14, [6, 26, 46, 66]),
		(15, [6, 26, 48, 70]),
		(16, [6, 26, 50, 74]),
		(17, [6, 30, 54, 78]),
		(18, [6, 30, 56, 82]),
		(19, [6, 30, 58, 86]),
		(20, [6, 34, 62, 90]),
		(21, [6, 28, 50, 72, 94]),
		(22, [6, 26, 50, 74, 98]),
		(23, [6, 30, 54, 78, 102]),
		(24, [6, 28, 54, 80, 106]),
		(25, [6, 32, 58, 84, 110]),
		(26, [6, 30, 58, 86, 114]),
		(27, [6, 34, 62, 90, 118]),
		(28, [6, 26, 50, 74, 98, 122]),
		(29, [6, 30, 54, 78, 102, 126]),
		(30, [6, 26, 52, 78, 104, 130]),
		(31, [6, 30, 56, 82, 108, 134]),
		(32, [6, 34, 60, 86, 112, 138]),
		(33, [6, 30, 58, 86, 114, 142]),
		(34, [6, 34, 62, 90, 118, 146]),
		(35, [6, 30, 54, 78, 102, 126]),
		(36, [6, 24, 50, 76, 102, 128]),
		(37, [6, 28, 54, 80, 106, 132]),
		(38, [6, 32, 58, 84, 110, 136]),
		(39, [6, 26, 54, 82, 110, 138]),
		(40, [6, 30, 58, 86, 114, 142])
	]

	BLACK = ord('x')
	WHITE = ord('.')
	UNKNW = ord('*')

	# Error Correction Level, mask, format string
	FORMATS = [
		('L', 0, 'xxx.xxxxx...x..'),
		('L', 1, 'xxx..x.xxxx..xx'),
		('L', 2, 'xxxxx.xx.x.x.x.'),
		('L', 3, 'xxxx...x..xxx.x'),
		('L', 4, 'xx..xx...x.xxxx'),
		('L', 5, 'xx...xx...xx...'),
		('L', 6, 'xx.xx...x.....x'),
		('L', 7, 'xx.x..x.xxx.xx.'),
		('M', 0, 'x.x.x.....x..x.'),
		('M', 1, 'x.x...x..x..x.x'),
		('M', 2, 'x.xxxx..xxxxx..'),
		('M', 3, 'x.xx.xx.x..x.xx'),
		('M', 4, 'x...x.xxxxxx..x'),
		('M', 5, 'x......xx..xxx.'),
		('M', 6, 'x..xxxxx..x.xxx'),
		('M', 7, 'x..x.x.x.x.....'),
		('Q', 0, '.xx.x.x.x.xxxxx'),
		('Q', 1, '.xx.....xx.x...'),
		('Q', 2, '.xxxxxx..xx...x'),
		('Q', 3, '.xxx.x......xx.'),
		('Q', 4, '.x..x..x.xx.x..'),
		('Q', 5, '.x....xx.....xx'),
		('Q', 6, '.x.xxx.xx.xx.x.'),
		('Q', 7, '.x.x.xxxxx.xx.x'),
		('H', 0, '..x.xx.x...x..x'),
		('H', 1, '..x..xxx.xxxxx.'),
		('H', 2, '..xxx..xxx..xxx'),
		('H', 3, '..xx..xxx.x....'),
		('H', 4, '....xxx.xx...x.'),
		('H', 5, '.....x..x.x.x.x'),
		('H', 6, '...xx.x....xx..'),
		('H', 7, '...x.....xxx.xx')
	]

	# bit encryption modes
	MODES = {
		'0001':'numeric',
		'0010':'alphanumeric',
		'0100':'byte',
		'1000':'kanji',
		'0000':'terminator'
	}

	ALPHANUM = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'

	@staticmethod
	def get_char_count_ind_len(mode, version):
		mode = 4-mode.find('1') # fix this but too lazy now
		# I first wrote as 1 2 3 4 then converted to 0001 strings upper line is a quick fix
		if version < 10:
			if mode == 1: return 10
			if mode == 2: return 9
			if mode == 3: return 8
			if mode == 4: return 8
		if version < 27:
			if mode == 1: return 12
			if mode == 2: return 11
			if mode == 3: return 16
			if mode == 4: return 10
		if mode == 1: return 14
		if mode == 2: return 13
		if mode == 3: return 16
		if mode == 4: return 12

	def __init__(self, path=None):
		self.dirty = True
		self.N = -1
		self.qr = []
		# corner position
		self.pos_finderp = [] # 0: LT, 1: RT, 2: LB, 3: LT as in FINDER_POS
		# align position
		self.pos_align = [] # 0,1,... depends on version
		if path is not None:
			self.load_qr(path)

	def get_qr(self):
		return self.qr

	@staticmethod
	def print_qr(qr):
		print(f"\n{'\n'.join([ ''.join(x) for x in qr])}\n")

	# '*' in mstr will ignored cstr can't have '*'
	@staticmethod
	def _qstr_match(cstr, mstr):
		cstr = ''.join(cstr)
		mstr = ''.join(mstr)
		for a, b in zip(cstr, mstr):
			if a != '*' and a != b:
				return False
		return True

	@staticmethod
	def size2version(N):
		error = 'Size is invalid must be N = (4*version + 17) and NxN N='+str(N)
		N -= 17
		if N % 4 != 0:
			raise MalformedFQRException(error)
		N //= 4
		if N < 0 or N > 40:
			raise MalformedFQRException('Unknown version: ' + N)
		return N

	@staticmethod
	def version2size(N):
		return 4*N+17

	# if path is set save image to path
	@staticmethod
	def save_qr_img(qr, path=None):
		dqr = qr[:, :] # copy
		dqr[dqr == 'x'] = '0' # turn str array to color array
		dqr[dqr == '.'] = '1'
		dqr[dqr == '*'] = '2'
		dqr = dqr.astype(np.uint32)
		dqr[dqr == 0] = 0
		dqr[dqr == 1] = 255
		dqr[dqr == 2] = 128
		from PIL import Image
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

	def load_qr(self, path):
		self.dirty = True
		with open(path, 'r') as f:
			# read non empty lines, erase end of lines
			self.qr = np.array([ list( x.strip('|\n').lower() ) for x in f.readlines() if len(x)>1])
			self.N = len(self.qr)
			self.version = FQR.size2version(self.N)
			print(f"Version: {self.version}\nSize: {self.N}x{self.N}\n")

			error = ''
			for line in self.qr:
				print(''.join(line))
				if len(line) != self.N:
					error = 'Dimensions does not match: line_len, N: '+str(len(line))+', '+str(self.N)
				elif any(ch not in 'x.*' for ch in line):
					error = 'Not allowed character(s): ' + ', '.join([ch for ch in line if ch not in 'x.*'])
				if error != '':
					raise MalformedFQRException(error)

			self.dirty = False
			self.bc_qr = self.qr[:, :] # take a copy for reversing
		print(f'FQR file loaded successfully:{path}\n')


	# TODO: make this accept a percentage of matches i.e there can be * in there
	# TODO: add this timing finder as well so as to more accurate results
	def find_positioning(self):
		s_qr = self.qr[:7, :7]
		if np.array_equal(FQR.FINDER_POS_PATTERN, s_qr):
			print('Position found: LT')
			self.pos_finderp.append(0)

		s_qr = self.qr[:7, -7:]
		if np.array_equal(FQR.FINDER_POS_PATTERN, s_qr):
			print('Position found: RT')
			self.pos_finderp.append(1)

		s_qr = self.qr[-7:, :7]
		if np.array_equal(FQR.FINDER_POS_PATTERN, s_qr):
			print('Position found: LB')
			self.pos_finderp.append(2)

		s_qr = self.qr[-7:, -7:]
		if np.array_equal(FQR.FINDER_POS_PATTERN, s_qr):
			print('Position found: RB')
			self.pos_finderp.append(3)

		# get not found corners
		miss_finder = [x for x in range(4) if x not in self.pos_finderp]
		return miss_finder

	# assumes alignment is found
	# need to check other format positions currently only RT is checked
	def find_format(self):
		fstr = ''.join(self.qr[8, -8:])
		res = []
		for f in FQR.FORMATS:
			print(f)
			print(fstr)
			print(f[2][-len(fstr):])
			print()
			if self._qstr_match(f[2][-len(fstr):], fstr):
				res.append(f)
		return res

	def fix_rotation(self, align, qr=None):
		if qr is None:
			qr = self.qr
		num_turns = [2, 1, 3, 0]
		qr = np.rot90(qr, num_turns[align])

	# assumes rotation is already fixed and fixes finder patterns
	def fix_position_patterns(self, qr=None):
		if qr is None:
			qr = self.qr
		#fix LT
		qr[:7, :7] = FQR.FINDER_POS_PATTERN[:, :]
		for i in range(8):
			qr[7][i] = qr[i][7] = '.'
		# fix RT
		qr[:7, -7:] = FQR.FINDER_POS_PATTERN[:, :]
		for i in range(8):
			qr[7][-i-1] = qr[i][  -8] = '.'
		# fix LB
		qr[-7:, :7] = FQR.FINDER_POS_PATTERN[:, :]
		for i in range(8):
			qr[-i-1][7] = qr[-8][i] = '.'
		# RB is always empty

	def fix_finder_patterns(self, qr=None):
		if qr is None:
			qr = self.qr
		pass

	def fix_timing_patterns(self, qr=None):
		if qr is None:
			qr = self.qr
		for i in range(7, len(qr)-7):
			p = ('x' if i%2 == 0 else '.')
			qr[i][6] = qr[6][i] = p

	def fix_format(self, f, qr=None):
		if qr is None:
			qr = self.qr
		fs = np.array(list(f))
		print('Fixing format with:', fs)
		qr[8, :6] = fs[:6]
		qr[8, 7:9] = fs[6:8]
		qr[7, 8] = fs[8]
		qr[8, -8:] = fs[-8:]
		qr[:6, 8] = np.transpose(fs[-6:])[::-1]
		qr[-7:, 8] = np.transpose(fs[:7])[::-1]

	def fix_alignment_patterns(self, qr=None):
		if qr is None:
			qr = self.qr
		if len(qr) <= 21: # these dont have align patterns
			return
		locs = None
		for l in FQR.ALIGN_PATTERN_LOC:
			if self.version == l[0]:
				locs = l[1]
				break
		loc1 = locs[0] # first loc
		locN = locs[len(locs)-1] # last loc
		for i in locs:
			for j in locs:
				if i == loc1 and (j == loc1 or j == locN):
					continue
				elif i == locN and j == loc1:
					continue
				qr[i-2:i+3, j-2:j+3] = FQR.ALIGN_PATTERN[:, :]

	def fix_dark_module(self, qr=None):
		if qr is None:
			qr = self.qr
		qr[4*self.version+9][8] = 'x'

	@staticmethod
	def get_next_bit(qr):
		N = len(qr)
		j = N-1
		while j > 0:
			if j == 6: # skip vertical timing patt.
				j -= 1
			for i in range(N-1, -1, -1):
				yield i, j
				yield i, j-1
			j -= 2
			for i in range(0, N, 1):
				yield i, j
				yield i, j-1
			j -= 2


	def try_read(self):
		# generate protected area of qr code by mimicing fixes
		pr_qr = np.zeros(self.qr.shape, dtype=str)
		self.fix_dark_module(pr_qr)
		self.fix_dark_module(pr_qr)
		self.fix_position_patterns(pr_qr)
		self.fix_alignment_patterns(pr_qr)
		self.fix_finder_patterns(pr_qr)
		self.fix_timing_patterns(pr_qr)
		self.fix_format('...............', pr_qr)
		# convert string to truth values
		is_data = (pr_qr == '')
		mask = get_mask(self.format[1])
		d = ''
		for i, j in FQR.get_next_bit(self.qr):
			if not is_data[i][j]:
				continue
			c = self.qr[i][j]
			m = mask(i, j)
			if not m:
				d += c
			elif c == 'x':
				d += '.'
			else:
				d += 'x'

		### TODO find a better solution for here sinde data segments are constant
		ds = d[:26*8].replace('x', '1').replace('.', '0')
		# re arrange d1-d13 and d14-d26
		d = ''
		for i in range(0, len(ds), 16):
			d += ds[i:i+8]
		for i in range(8, len(ds), 16):
			d += ds[i:i+8]
		ds = d
		print('Read valid data: ', ds)
		LDS = len(ds)
		k = 0
		res = ''
		while k < LDS:
			mode = ds[k:k+4]
			k += 4
			print(k, 'Read: ', ds[:k])
			ds = ds[k:]
			k = 0
			if mode not in FQR.MODES:
				raise TypeError('Bits are broken unknown mode: '+mode)
			if mode == '0000':
				print('Found:', res)
				return res

			print('Mode:', FQR.MODES[mode])
			ind_len = FQR.get_char_count_ind_len(mode, self.version)
			char_cnt = bin_ar_to_int(ds[k:k+ind_len])
			k += ind_len
			print('Ind len:', ind_len)
			print('Char count:', char_cnt)

			if mode == '0001': # numeric
				for t in range(char_cnt):
					raise NotImplementedError('will look how to do later')
					k += 3
			elif mode == '0010': # alphanumeric
				for t in range(char_cnt//2):
					x = bin_ar_to_int(ds[k:k+11])
					x1 = x//45
					x2 = x%45
					c1 = FQR.ALPHANUM[x1]
					res += c1
					c2 = FQR.ALPHANUM[x2]
					res += c2
					print('ch1:', c1, x1)
					print('ch2:', c2, x2)
					k += 11
				if char_cnt % 2 == 1:
					x = bin_ar_to_int(ds[k:k+11])
					print('ch3:', FQR.ALPHANUM[x], x)
					res += FQR.ALPHANUM[x]
					k += 11
			elif mode == '0100': # byte
				for t in range(char_cnt):
					x = bin_ar_to_int(ds[k:k+8])
					c = chr(x)
					res += c
					k += 8
					print('ch0:', c, x, ds[k-8:k])
			elif mode == '1000': # kanji
				raise NotImplementedError('will look how to do later (sorry you bumped into one using :)')

	def fix_qr(self):
		poses = self.find_positioning()
		poses = [3]
		for p in poses:
			print('Trying alignment:', p)
			bc_qr = self.qr[:, :]
			self.fix_rotation(p)
			self.fix_dark_module()
			self.fix_position_patterns()
			self.fix_alignment_patterns()
			self.fix_finder_patterns()
			self.fix_timing_patterns()
			fmts = self.find_format()
			if len(fmts) == 0:
				print('no matching format for: ', p)
				continue
			for f in fmts:
				print('Trying format:', f)
				fbc_qr = self.qr[:, :]
				self.format = f
				self.fix_format(self.format[2])
				res = self.try_read()
				if res is not None:
					return res
				self.qr = fbc_qr
			self.qr = bc_qr

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help='FQR file to fix')
	parser.add_argument('-g','--gen-qr', action='store', type=int, help='generate empty fqr matrix')
	parser.add_argument('--show-format', action='store_true', help='shows fqr matrix format')
	args = parser.parse_args()

	if len(sys.argv) == 1:
		parser.print_help()
		sys.exit(0)

	if args.gen_qr:
		N = args.gen_qr
		if N < 1: N = 1
		if N > 40: N = 40
		N = N*4+17
		qr = [['*' for col in range(N)] for row in range(N)]
		qr_str = '\n'.join([''.join(s) for s in qr])+'\n'
		if args.file:
			with open(args.file, 'w') as f:
				f.write(qr_str)
		else:
			print(qr_str)
		sys.exit(0)

	if args.show_format:
		print_fqr_format()
		sys.exit(0)

	fqr = FQR(args.file)

	res = fqr.fix_qr()
	print('Result:', res)
	#fqr.print_qr(fqr.get_qr())
	FQR.save_qr_img(fqr.get_qr(), args.file+'-fixed.png')

'''
TODO LIST
* for each possible fqr matrix we will try to fix it by
** trying possible missing bits
** give possible results (with filters such as visible ascii)
'''
