from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="api-test-generator",
    version="1.0.0",
    author="Asko - AI Assistant",
    author_email="asko@openclaw.ai",
    description="OpenAPI/Swagger belirtimlerinden otomatik API test kodları üretme aracı",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/api-test-generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.5.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.25.0",
        "jinja2>=3.1.0",
        "pyyaml>=6.0.1",
        "click>=8.1.0",
        "rich>=13.7.0",
        "jsonschema>=4.20.0",
        "openapi-spec-validator>=0.7.0",
        "faker>=20.1.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.2.0",
    ],
    extras_require={
        "dev": [
            "pytest-html>=4.1.0",
            "pytest-xdist>=3.5.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "api-test-generator=api_test_generator.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="api testing openapi swagger test automation codegen",
    project_urls={
        "Bug Reports": "https://github.com/openclaw/api-test-generator/issues",
        "Source": "https://github.com/openclaw/api-test-generator",
        "Documentation": "https://github.com/openclaw/api-test-generator/wiki",
    },
)