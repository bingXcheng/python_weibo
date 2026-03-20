from setuptools import setup, find_packages

setup(
    name="weibo_spider",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'sqlalchemy',
        'pymysql'
    ]
)