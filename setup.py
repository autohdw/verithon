# setup.py
from setuptools import setup, find_packages

setup(
    name='verithon',
    version='0.3',
    packages=find_packages(),
    description='RTL Auto-generation with Verilog Embedded in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='JiaYanXu',
    author_email='jiayanxu@seu.edu.cn',
    url='https://github.com/autohdw/Voldelog.git',
    license='MIT',
    python_requires='>=3.6',
)
