#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require={
    "Conversion": ["cairosvg>=2.7.0"],
},

# fix accidental uppercasing in v0.4.0
extras_require["conversion"] = extras_require["Conversion"]

# Add a group made up of all optional dependencies
extras_require["all"] = {
    package for group in extras_require.values() for package in group
}

setup(name='svgling',
    version='0.4.0',
    description='Linguistic tree diagrams in python + svg',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Kyle Rawlins',
    author_email='kgr@jhu.edu',
    license='MIT',
    url='https://rawlins.github.io/svgling/',
    project_urls={
        'Repository': 'https://github.com/rawlins/svgling',
    },
    install_requires='svgwrite',
    extras_require=extras_require,
    python_requires='>=3',
    packages=['svgling'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Environment :: Web Environment"]
    )
