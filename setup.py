#!/usr/bin/env python3
"""
Setup script for Sweet Progress - Save Game Backup Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sweet-progress",
    version="2.5.6",
    author="Smothyze",
    author_email="smothyze@gmail.com",
    description="A Python-based GUI application for backing up game save files",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Smothyze/sweet-progress",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "sweet-progress=program:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.png", "*.ico", "*.txt"],
    },
    keywords="game, backup, save, files, gui, tkinter",
    project_urls={
        "Bug Reports": "https://github.com/Smothyze/sweet-progress/issues",
        "Source": "https://github.com/Smothyze/sweet-progress",
        "Documentation": "https://github.com/Smothyze/sweet-progress#readme",
    },
) 