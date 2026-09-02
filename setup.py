from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="responsa",
    version="1.0.0",
    description="Ferramenta OSINT em Python com buscas de username, e-mail, CEP, telefone, nome e IP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Seu Nome",
    url="https://github.com/alairon330-rgb/responsa",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={"responsa": ["data/*.json"]},
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "phonenumbers>=8.13.0",
        "dnspython>=2.4.0",
        "duckduckgo-search>=5.0.0",
        "colorama>=0.4.6",
        "pillow>=10.0.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "responsa=responsa.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Intended Audience :: Information Technology",
    ],
)
