# pylint: disable=missing-module-docstring
import re
import setuptools


with open("liquid/__init__.py", "r") as fd:
    match = re.search(r'__version__ = "([0-9\.]+)"', fd.read())
    assert match is not None
    __version__ = match.group(1)

with open("README.rst", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="python-liquid",
    version=__version__,
    description="A Python engine for the Liquid template language.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://jg-rp.github.io/liquid/",
    packages=setuptools.find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["python-dateutil>=2.8.1"],
    extras_require={"autoescape": ["MarkupSafe>=2.0.0"]},
    test_suite="tests",
    python_requires=">=3.7",
    licence="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    project_urls={
        "Documentation": "https://jg-rp.github.io/liquid/",
        "Issue Tracker": "https://github.com/jg-rp/liquid/issues",
        "Source Code": "https://github.com/jg-rp/liquid",
        "Change Log": "https://github.com/jg-rp/liquid/blob/main/CHANGES.rst",
    },
)
