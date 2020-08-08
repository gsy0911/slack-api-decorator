import setuptools
import os


def get_version(init_file_path):
    version_line = list(
        filter(lambda l: l.startswith('VERSION'), open(init_file_path))
    )[0]

    # eval is required to convert from string to tuple,
    # because VERSION defined in __init__.py is tuple
    version_tuple = eval(version_line.split('=')[-1])

    # join with dot
    return ".".join(map(str, version_tuple))


# get __version__ from __init__.py
init = os.path.join(
    os.path.dirname(__file__), 'slack_api_decorator', '__init__.py'
)
VERSION = get_version(init_file_path=init)

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="slackapidecorator",
    version=VERSION,
    author="gsy0911",
    author_email="yoshiki0911@gmail.com",
    description="slack api decorator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gsy0911/slack-api-decorator",
    packages=setuptools.find_packages(),
    install_requires=[],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
    keywords=["slack", "slack-api", "slash-command", "event-subscription"]
)
