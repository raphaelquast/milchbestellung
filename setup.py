# -*- coding: UTF-8 -*-

"""
setup file for milchbestellung
"""

from setuptools import setup
from setuptools import find_packages

install_requires = ["numpy", "pandas"]

setup(name='milchbestellung',
      version='v0.0.1',
      description='milchbestellung',
      package_dir={'milchbestellung': 'milchbestellung'},
      install_requires=install_requires,
      )


