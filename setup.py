import re
import setuptools


with open("liquid/__init__.py", "r") as fd:
    match = re.search(r'__version__ = "([0-5\.]+)"', fd.read())
    __version__ = match.group(1)

with open("README.rst", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="Liquid",
    version=__version__,
    description="Render Liquid templates",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jg-rp/liquid",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["python-dateutil>=2.8.1"],
    test_suite="tests",
    python_requires=">=3.8",
)
