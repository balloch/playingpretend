"""
setup file for the pretender package
"""

import setuptools


with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pretender",
    version="0.0.1",
    packages=setuptools.find_packages(),
    author="Jonathan Balloch",
    author_email="jon.balloch@gmail.com",
    description="A package for generating tabletop RPG adventures.")
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # url="

