import re
import setuptools


with open("liquid/__init__.py", "r") as fd:
    match = re.search(r'__version__ = "([0-9\.]+)"', fd.read())
    __version__ = match.group(1)

with open("README.rst", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="python-liquid",
    version=__version__,
    description="A Python template engine for the Liquid markup language.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jg-rp/liquid",
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["python-dateutil>=2.8.1"],
    test_suite="tests",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
