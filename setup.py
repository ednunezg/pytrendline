from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="primelib-ednunezg",
    version="0.0.1",
    author="Eduardo Nunez",
    author_email="ed@ednunez.me",
    description="Detection for support and resistance trendlines on python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ednunezg/pytrendline",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
