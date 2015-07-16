from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension("chromakey", ["chromakey.pyx"],
        include_dirs = [numpy.get_include()])
]
setup(
    name = "chromakey",
    ext_modules = cythonize(extensions),
)