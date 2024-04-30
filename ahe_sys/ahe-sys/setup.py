# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__version__ = '0.1.1'


setup(
    name='ahe_sys',
    version=__version__,
    description='Base project to group diffrent setup',
    author='Rohit Gupta',
    author_email='rohit_gupta@amperehourenergy.com',
    include_package_data=True,
    url='https://gitlab.com/amperehourenergy/ahe_sys.git',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: AHE License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
)
