#!/usr/bin/env python
from setuptools import setup, find_packages

requires = [
    'aioauth-client',
    'cryptography',
    'aiohttp>=3.4.0',
    'aiohttp_session>=2.7.0'
    'pyJWT'
]

setup_options = dict(
    name='aiohttp_oauth',
    version='0.9.0',
    description='oauth middleware for aiohttp',
    long_description='See readme at '
                     'https://github.com/CanopyTax/aiohttp-oauth',
    author='nhumrich',
    author_email='nick@humrich.us',
    packages=find_packages('.'),
    package_dir={'aiohttp_oauth': 'aiohttp_oauth'},
    url='https://github.com/CanopyTax/aiohttp-oauth',
    install_requires=requires,
    license="Apache",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)

setup(**setup_options)
