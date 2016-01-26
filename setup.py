# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

long_description = open(os.path.join(here, 'README.rst')).read()

# allow setup.py to be run from any path
#os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='python-aqi',
    version="0.5.1",
    author="Stefan \"hr\" Berder",
    author_email="hr@bonz.org",
    license="BSD 3-Clause",
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    url='https://github.com/hrbonz/python-aqi',
    description='A library to convert between AQI value and pollutant '
    'concentration (µg/m³ or ppm)',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    keywords='air quality pm2.5 EPA MEP',
    entry_points = {
        'console_scripts': [
            'aqi=aqi:console_aqi',
        ],
    },
)
