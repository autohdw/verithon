# setup.py
from setuptools import setup, find_packages

setup(
    name='PyTV',
    version='0.1',
    packages=find_packages(),
    description='RTL Auto-generation with Verilog Embedded in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='JiaYan Xu',
    author_email='jiayanxu@.com',
    url='https://github.com/yourusername/simplemath',
    license='MIT',
    python_requires='>=3.6',
)
