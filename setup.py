from setuptools import setup

version = "0.2.0"

with open("README.md") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().split("\n")

setup(
    name="discord-ext-wizard",
    author="FalseDev",
    author_email="59121948+FalseDev@users.noreply.github.com",
    version=version,
    url="https://github.com/FalseDev/discord-ext-wizard",
    packages=["discord.ext.wizard"],
    license="MIT",
    description="A Discord.py extension that makes setup wizards too easy.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extras_require=None,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
