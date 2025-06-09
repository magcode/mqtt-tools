from setuptools import setup, find_packages

setup(
    name="malog",
    version="0.1.0",
    description="A logging utility with Loki and colorlog support.",
    author="magod",
    packages=find_packages(),
    install_requires=[
        "colorlog",
        "logging_loki"
    ],
    python_requires=">=3.6",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
