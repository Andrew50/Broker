from setuptools import setup
from Cython.Build import cythonize
import numpy
# Use python setup.py build_ext --inplace 
# from C:/dev/Broker
setup(
    ext_modules = cythonize("backend/Odtw.pyx"),
    include_dirs=[numpy.get_include()]
)
