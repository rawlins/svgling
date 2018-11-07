#!/usr/bin/env python

from distutils.core import setup

setup(name='svgling',
      version='0.1',
      description='SVG+Python based rendering of linguistics-style (constituent) trees',
      author='Kyle Rawlins',
      author_email='kgr@jhu.edu',
      license='MIT',
      url='https://github.com/rawlins/svgling',
      install_requires='svgwrite',
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
