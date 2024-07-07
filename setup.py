from setuptools import setup, find_packages
from setuptools.command.install import install
import pathlib

here = pathlib.Path(__file__).parent.resolve()

VERSION = '0.0.1'
DESCRIPTION = 'EA FC 24 SBC solver'
LONG_DESCRIPTION = (here / "README.md").read_text(encoding="utf-8")

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="eafc24-ut-players",
    version=VERSION,
    author="Bartlomiej Niemiec",
    author_email="<bniemiec11@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url="https://github.com/bartlomiej-niemiec/fc24-sbc-solver",
    packages=find_packages(where="src"),
    install_requires=[
        "ortools",
        "pandas",
        "sqlite3",
        "sqlalchemy"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=[
        'google or-tools',
        'mixed-integer-programming',
        'cp-sat',
        'python',
        'eafc24',
        'ultimate team',
        'sbc'
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    package_dir={"": "src"},
)