# setup.py
from setuptools import setup, find_packages

setup(
    name='pytv',
    version='0.1',
    packages=find_packages(),
    description='Simple math operations',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='JiaYan Xu',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/simplemath',
    license='MIT',
    python_requires='>=3.6',
)
