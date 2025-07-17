"""
DocGenius Package Setup Configuration
Professional Python Package for Document Generation
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

# Read requirements from requirements.txt
requirements = []
if os.path.exists('requirements.txt'):
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="docgenius",
    version="1.0.0",
    author="Bruno Pineda", 
    author_email="",
    description="Professional document generation toolkit with modular, extensible architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brunovskyy/file-generator",
    project_urls={
        "Bug Tracker": "https://github.com/brunovskyy/file-generator/issues",
        "Documentation": "https://github.com/brunovskyy/file-generator/blob/main/README.md",
        "Source Code": "https://github.com/brunovskyy/file-generator",
    },
    packages=find_packages(exclude=['tests*', 'tools*', '.dev*', 'build*', 'dist*']),
    package_data={
        'docgenius': [
            'logic/*/README.md',
            'logic/*/*/*.py',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    keywords="document generation, pdf, word, markdown, data processing, templates, automation",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
        'full': [
            'pytest>=7.0.0',
            'black>=22.0.0', 
            'flake8>=4.0.0',
            'mypy>=0.950',
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'docgenius=app_launcher_cli:main',
            'docgenius-dev=docgenius.cli.dev_tools:main',
            'docgenius-system=docgenius.cli.system_tools:main',
        ],
    },
    zip_safe=False,
    platforms=['any'],
    license='MIT',
    license_files=['LICENSE'] if os.path.exists('LICENSE') else [],
)
