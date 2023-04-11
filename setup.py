from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import numpy

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html
ext = '.pyx' if USE_CYTHON else '.c'
extensions = [
    Extension(
        name="alqalign.ctc_segmentation.ctc_segmentation_dyn",
        sources=["alqalign/ctc_segmentation/ctc_segmentation_dyn"+ext],
        include_dirs=[numpy.get_include()],
    )
]
if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)


def get_requirements():
    """
    Return requirements as list.

    package1==1.0.3
    package2==0.0.5
    """
    with open('requirements.txt') as f:
        packages = []
        for line in f:
            line = line.strip()
            # let's also ignore empty lines and comments
            if not line or line.startswith('#'):
                continue
            packages.append(line)
    return packages



setup(
   name='alqalign',
   version='1.1.4',
   description='a text-speech alignment model',
   author='Xinjian Li',
   author_email='xinjianl@cs.cmu.edu',
   packages=find_packages(exclude=["tests"]),
   setup_requires=["numpy"],
   url="https://github.com/xinjli/alignspeech",
   install_requires=get_requirements(),
    zip_safe=False,
    ext_modules=extensions,
    cmdclass={'build_ext': build_ext},
)
