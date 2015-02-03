from setuptools import setup, find_packages
from skald import __version__ as version

setup(
    name="skald",
    version=version,
    description="Automatically generate website documentation",
    url="https://github.com/bjornarg/skald",
    author="Bjørnar Grip Fjær",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.4",
    ],
    keywords="documentation",
    packages=find_packages(),
    install_requires=["Pillow"],
    entry_points={
        "console_scripts": [
            "skald=skald.main:main"
        ],
    },
)
