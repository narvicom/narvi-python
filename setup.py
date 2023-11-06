import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

version_contents = {}
with open(os.path.join(here, "narvi", "version.py"), encoding="utf-8") as f:
    exec(f.read(), version_contents)

setup(
    name="narvi",
    author="Narvi Payments Oy Ab ",
    version=version_contents["VERSION"],
    packages=find_packages(),
    description="Narvi API library",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/narvicom/narvi-python",
    install_requires=[
        'requests',
        'cryptography',
        'canonicaljson',
    ],
)