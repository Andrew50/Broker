from setuptools import setup
from Cython.Build import cythonize
import numpy
# run the following commands -----------------
# cd C:/dev/Broker/backend
# python setup.py build_ext --inplace 
#or>>>>>>>>>
# py setup.py build_ext --inplace 

setup(
    ext_modules = cythonize("tasks/Odtw.pyx"),
    include_dirs=[numpy.get_include()]
)
