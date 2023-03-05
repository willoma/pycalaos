from distutils.core import setup

setup(
    name="pycalaos",
    version="0.0.1",
    description="Calaos home automation client library",
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
