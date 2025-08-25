from setuptools import setup, find_packages

setup(
    name="osmxmpp",
    version="0.1.0",

    author="osmiumnet",
    description="Python XMPP library",

    packages=find_packages(),
    install_requires=[
        'osmxml==0.1.0'
    ],
    python_requires=">=3.10",
)