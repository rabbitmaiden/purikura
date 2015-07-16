#!/usr/bin/python
import numpy
cimport numpy
from libc.math cimport sqrt

cdef double colorclose(int Cb_p, int Cr_p) nogil:
  cdef int Cb_key, Cr_key
  cdef double tola, tolb, cb2, cr2, temp
  Cb_key = 92
  Cr_key = 86
  tola = 44.0
  tolb = 52.0
  cb2 = (Cb_key-Cb_p) * (Cb_key-Cb_p)
  cr2 = (Cr_key-Cr_p) * (Cr_key-Cr_p)
  temp = cb2 + cr2
  temp = sqrt(temp)

  if temp < tola:
    return 0
  elif (temp < tolb):
    return (temp-tola)/(tolb-tola)
  else:
    return 1


cpdef numpy.ndarray chromakey(fg, bg):

  cdef int i, j, Cb_p, Cb_r, xsize, ysize
  cdef double mask
  cdef list irange, jrange, krange

  fg_rgb = numpy.array(fg)
  fg_ycbcr = fg.convert("YCbCr")
  fg_ycbcr = numpy.ndarray((fg.size[1], fg.size[0], 3), 'u1', fg_ycbcr.tostring())

  bg_rgb = numpy.array(bg)

  xsize = len(fg_rgb)
  ysize = len(fg_rgb[0])
  out = numpy.zeros((xsize,ysize,3))
  out = out.astype('uint8')

  irange = range(0,xsize)
  jrange = range(0,ysize)
  krange = range(0,3)

  for i in irange:
    for j in jrange:
      Cb_p = int(fg_ycbcr[i][j][1])
      Cb_r = int(fg_ycbcr[i][j][2])

      mask = 1-colorclose(Cb_p, Cb_r)

      if mask == 0:
        out[i][j] = fg_rgb[i][j]
      elif mask == 1:
        out[i][j] = bg_rgb[i][j]
      else:
        maskarray = [mask, mask, mask]
        out[i][j] = fg_rgb[i][j] - (mask * fg_rgb[i][j]) + (bg_rgb[i][j] * mask)

  return out