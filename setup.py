#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="pollen-visualization",
    version="0.1.0",
    description="花粉数据分析与可视化工具",
    author="SPI2 Team",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.3.0",
        "pandas>=1.1.0",
        "numpy>=1.19.0",
        "seaborn>=0.11.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=20.8b1",
            "flake8>=3.8.0",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "pollen-viz=pollen_viz:main",
            "pollen-data=pollen_data_tool:main",
        ],
    },
) 