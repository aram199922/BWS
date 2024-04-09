import pathlib
from setuptools import setup, find_packages

'''
with open('requirements.txt', 'r') as file:    
    lines = [line.strip() for line in file.readlines()]
install_requires = [line for line in lines]
'''

setup(
    name="myBWS",
    description="Tool for conducting and analyzing best-worst scaling surveys",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Aram Barseghyan, Sergo Poghosyan, Arevik Papikyan, Nare Stepanyan, Elen Sukiasyan",
    classifiers=[
        "Development Status :: 3 - Alpha"
    ],
    python_requires=">=3.10, <3.12", 
    install_requires = [
        "annotated-types==0.6.0",
        "anyio==4.3.0",
        "click==8.1.7",
        "colorama==0.4.6",
        "fastapi==0.110.0",
        "ghp-import==2.1.0",
        "idna==3.6",
        "Jinja2==3.1.3",
        "Markdown==3.6",
        "MarkupSafe==2.1.5",
        "mergedeep==1.3.4",
        "mkdocs==1.5.3",
        "numpy==1.26.4",
        "packaging==24.0",
        "pandas==2.2.1",
        "pathspec==0.12.1",
        "platformdirs==4.2.0",
        "pydantic==2.6.4",
        "pydantic_core==2.16.3",
        "pyreadr==0.5.0",
        "python-dateutil==2.9.0.post0",
        "pytz==2024.1",
        "PyYAML==6.0.1",
        "pyyaml_env_tag==0.1",
        "six==1.16.0",
        "sniffio==1.3.1",
        "starlette==0.36.3",
        "typing==3.7.4.3",
        "typing_extensions==4.10.0",
        "tzdata==2024.1",
        "watchdog==4.0.0"
    ],
    packages=find_packages(include=["BWS", 'BWS.*']),
    version = "0.0.1"  
)
