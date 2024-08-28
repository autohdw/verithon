from setuptools import setup, find_packages

setup(
    name='pytv',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pytv=src.main:main',  # "myhello" 是命令行工具的名称，"myhello.hello:main" 指 myhello 包里的 hello.py 文件中的 main 函数
        ],
    },
)
