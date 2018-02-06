
import sys
import os
from setuptools import setup, find_packages


setup(
	name='rocketchat',
	version='0.1',
	description='Python api wrapper for the rocket.chat REST API',
	author='Brendan Abel',
	author_email='007brendan@gmail.com',
	packages=find_packages(),
    zip_safe=False,
)