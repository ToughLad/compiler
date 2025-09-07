#!/usr/bin/env python3
"""Setup script for LINE Thrift Compiler"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="line-thrift-compiler",
    version="1.0.0",
    author="LINE Thrift Compiler Contributors",
    description="Thrift IDL extractor and compiler for LINE APK decompiled sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toughlad/compiler",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pathlib2>=2.3.0",
    ],
    entry_points={
        "console_scripts": [
            "line-thrift-compiler=thrift_compiler:main",
        ],
    },
)
