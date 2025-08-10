from setuptools import setup, find_packages

setup(
    name="vehicle-registration-dashboard",
    version="1.0.0",
    author="Backend Developer Intern",
    description="Interactive dashboard for vehicle registration data analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "plotly>=5.15.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "numpy>=1.24.0",
        "python-dateutil>=2.8.0",
        "openpyxl>=3.1.0",
        "xlrd>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "flake8>=6.0.0",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
