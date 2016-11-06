import pytest
import os
from fqrfixer import FQR

def test_fqrfixer():
	fqr = FQR('examples/qr-easy.fqr')
	res = fqr.fix_qr()
	assert(res == 'SECCON{PSwIQ9d9GjKTdD8H}')

def test_fqrfixer_saveimg():
	fqr = FQR('examples/qr-easy.fqr')
	fqr.fix_qr()
	test_path = '/tmp/testing-qr-res.png'
	FQR.save_qr_img(fqr.get_qr(), test_path)
	assert(os.path.exists(test_path))
	os.remove(test_path)
