f-qr-fixer
=========

![Python 2.7|3.4|3.5](https://img.shields.io/badge/python-2.7%7C3.4%7C3.5-blue.svg) [![Build Status](https://travis-ci.org/fmakdemir/f-qr-fixer.svg?branch=master)](https://travis-ci.org/Fmakdemir/f-qr-fixer)

QR fixer part is standalone but for image to FQR conversion it requires Pillow (can be installed with easy_install), qrtools (on ubuntu there is a python-qrtools package)

Using a file given in format of an NxN matrix where x or X is black . is white and * is unknown

For example an fqr input where left side of qr code is destroyed from SECCON-14/qr-easy:

```
****************XX....XXXXXXX
*****************.XXX.X.....X
****************XX.XX.X.XXX.X
****************X.X...X.XXX.X
*****************XX.X.X.XXX.X
*****************.X.X.X.....X
****************X.X.X.XXXXXXX
****************X...X........
*****************XX.XX.XXXXX.
****************XX.X.X.X....X
*****************X.X.X..XXXX.
*****************XX..X.XXXXXX
******************.X...XXX...
******************..X.XX.X.X.
******************...XXXXXXX.
******************..XX...X.X.
******************..XX.X..X.X
******************.XXX...X...
******************..X...X.X.X
******************...X..X..XX
******************.XXXXXX.XXX
******************..X...X...X
******************XXX.X.X.X..
******************XXX...X....
******************XXXXXXX.X.X
******************.X.X.X.XX..
******************.XXXX...XXX
******************XX...XX.X.X
******************.XX.XXXX.XX
```


Example usage:
```
./fqr-image2fqr.py examples/seccon.png 29 -o seccon
./fqr-fixer.py -f seccon.fqr
```
