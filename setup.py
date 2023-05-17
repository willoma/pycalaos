from distutils.core import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pycalaos",
    version="0.0.14",
    description="Calaos home automation client library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Sébastien Maccagnoni",
    author_email="sebastien@maccagnoni.eu",
    url="https://github.com/tiramiseb/pycalaos",
    packages=["pycalaos"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    requires=["netifaces"]
)
