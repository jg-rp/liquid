# from distutils.core import setup
# from distutils.extension import Extension
# from Cython.Build import cythonize

# setup(
#     ext_modules=cythonize(
#         [
#             Extension(
#                 "liquid.lexer",
#                 sources=["ext/lexer.pyx", "ext/src/lex.cpp"],
#             ),
#         ],
#         annotate=True,
#     )
# )

from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("liquid/clex.pyx", annotate=True))
