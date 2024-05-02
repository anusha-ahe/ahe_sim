# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__version__ = '0.1.1'

setup(
    name='ahe_log',
    version=__version__,
    description='ahe_log used for logging the log in database',
    author='Kanaiya Thakkar',
    author_email='kanaiya_thakkar@amperehourenergy.com',
    include_package_data=True,
    url='git@gitlab.com:amperehourenergy/ahe_log.git',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
)

# Usage of setup.py:
# $> python setup.py register             # registering package on PYPI
# $> python setup.py build sdist upload   # build, make source dist and upload to PYPI
