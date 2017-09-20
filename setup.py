#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='ashaw_notes',
      version='0.0.1',
      description='Note taking made easy',
      author='Adam Shaw',
      author_email='adamryanshaw@gmail.com',
      url='https://github.com/follower46/ashaw-notes',
      packages=find_packages(exclude="tests"),
      install_requires=[
      	'dateparser>=0.6.0',
		'fakeredis>=0.8.0',
		'logzero>=1.3.0',
		'redis>=2.10.0',
		'mock>=2.0.0',
		'ddt>=1.1.0',
		'PyQt5>=5.0',
		'python_dateutil>=2.6.0',
		'click>=6.0',
      ],
      entry_points = {
        'console_scripts': ['ashaw-notes=ashaw_notes.main:cli'],
    	}
     )
