from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("gen_ext_conf.py")
    )
