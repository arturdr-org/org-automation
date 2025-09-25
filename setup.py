#!/usr/bin/env python3
"""Setup script for org-automation package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "docs" / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="org-automation",
    version="2.0.0",
    author="arturdr-org",
    description="Complete organizational automation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "org-automation=core.automation.main:main",
            "org-monitor=core.monitoring.health_check:main", 
            "org-dashboard=core.monitoring.dashboard:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
