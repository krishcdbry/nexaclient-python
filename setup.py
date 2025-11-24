"""
Setup configuration for nexadb Python package
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read version
version = '1.0.0'

setup(
    name='nexadb',
    version=version,
    description='Official Python client for NexaDB - The high-performance, easy-to-use database',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='NexaDB Team',
    author_email='team@nexadb.dev',
    url='https://github.com/krishcdbry/nexadb-python',
    project_urls={
        'Documentation': 'https://nexadb.dev/docs',
        'Source': 'https://github.com/krishcdbry/nexadb-python',
        'Tracker': 'https://github.com/krishcdbry/nexadb-python/issues',
    },
    packages=find_packages(),
    install_requires=[
        'msgpack>=1.0.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='nexadb database nosql lsm-tree vector-search binary-protocol client high-performance',
    license='MIT',
)
