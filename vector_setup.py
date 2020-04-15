# python vector_setup.py build_ext --inplace

from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Vector class module',
    ext_modules=cythonize("vector.pyx"),
    zip_safe=False,
)
