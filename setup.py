from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pytrendline",
    version="1.0.0",
    author="Eduardo Nunez",
    author_email="ed@ednunez.me",
    description="Detection for support and resistance trendlines on python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ednunezg/pytrendline",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    platforms=['any'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    include_package_data=True,
    install_requires=[
        'numpy>=1.18.5',
        'pandas>=1.0.4',
        'datetime>=4.3',
        'bokeh>=2.0.2',
        'colour>=0.1.5',
    ]
)
