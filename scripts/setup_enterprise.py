#!/usr/bin/env python3
"""
🚀 AI-Powered Org Automation Suite - Enterprise Setup
Advanced setup configuration for the AI automation system
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-powered-AI-powered-org-automation-suite",
    version="1.0.0",
    author="arturdr-org",
    author_email="contact@arturdr-org.dev",
    description="Enterprise-grade AI-powered automation suite for GitHub organizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arturdr-org/AI-powered-AI-powered-org-automation-suite",
    project_urls={
        "Bug Tracker": "https://github.com/arturdr-org/AI-powered-AI-powered-org-automation-suite/issues",
        "Documentation": "https://github.com/arturdr-org/AI-powered-AI-powered-org-automation-suite/blob/main/docs/",
        "Source": "https://github.com/arturdr-org/AI-powered-AI-powered-org-automation-suite",
        "Changelog": "https://github.com/arturdr-org/AI-powered-AI-powered-org-automation-suite/releases",
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators", 
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-automation=scripts.demo_ai_system:main",
            "ai-manual=scripts.ai_manual_parser:main",
            "ai-hub=scripts.ai_integration_hub:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.json", "*.md", "*.txt"],
    },
    keywords="ai automation github enterprise claude openai gemini mcp devops cicd",
)
