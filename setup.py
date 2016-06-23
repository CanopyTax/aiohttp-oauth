#!/usr/bin/env python
from setuptools import setup, find_packages

requires = [
    'aioauth-client',
    'cryptography',
    'aiohttp',
    'aiohttp_session'
]

setup_options = dict(
    name='aiogithubauth',
    version='0.2.0',
    description='github auth middleware for aiohttp',
    long_description='See readme at https://github.com/CanopyTax/aiohttp-github-auth',
    author='nhumrich',
    author_email='nick@humrich.us',
    packages=find_packages('.'),
    package_dir={'aiogithubauth': 'aiogithubauth'},
    url='https://github.com/CanopyTax/aiohttp-github-auth',
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
