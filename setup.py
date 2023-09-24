#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='svgling',
    version='0.4.0',
    description='SVG+Python based rendering of linguistics-style (constituent) trees',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Kyle Rawlins',
    author_email='kgr@jhu.edu',
    license='MIT',
    url='https://github.com/rawlins/svgling',
    install_requires='svgwrite',
    extras_require={
        "Conversion": ["cairosvg>=2.7.0"],
    },
    python_requires='>=3',
    packages=['svgling'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        "Framework :: Jupyter",
        "Environment :: Web Environment"]
    )
