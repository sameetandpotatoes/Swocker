import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='Swocker',
      version='1.0',
      description='Get company tweets, predict company stocks',
      author='SIGIR Squad',
      author_email='',
      url='http://www.python.org/sigs/distutils-sig/',
     install_requires=required,
     )
