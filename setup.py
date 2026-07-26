from setuptools import setup
from setuptools import find_packages
from pathlib import Path



from os.path import join, dirname
from os import chdir, walk
from pathlib import Path
import flaskcbv.version
import sys


from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False


if len(sys.argv) and not dirname(sys.argv[0]) == '':
        chdir( dirname(sys.argv[0]) )



this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(

    author = 'procool',
    author_email = 'ya.procool@ya.ru',
    license = 'BSD 2 Clause',
    url = 'https://github.com/procool/flaskcbv/',

    name = "flaskcbv",
    description="FlaskCBV is Alternative Framework for working with flask with the class Based Views approach (CBV)",
    long_description=long_description,
    long_description_content_type='text/markdown',

    version = flaskcbv.version.__version__,
    packages = find_packages(),


    entry_points={
        'console_scripts':
        [
                'flaskcbv = flaskcbv.scripts.flaskcbv:main'
        ],
    },


    install_requires=[
        'setuptools',
        'Flask>=2.0',
        # Floor bumped from >=2.1 (2026-07-26): that range let pip resolve an
        # old vulnerable release (9 Dependabot findings — debugger RCE when
        # DEBUG=True, multipart-form DoS, safe_join Windows device-name
        # bypasses, nameless-cookie __Host- bypass). 3.1.6 is the first
        # release confirmed to include the safe_join fixes (the last of the
        # 9 to land); everything else was already fixed well before it.
        'Werkzeug>=3.1.6',
        'itsdangerous>=2.0',
    ],

    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-flask',
            'coverage',
            'ruff>=0.1.0',
        ],
    },

    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],

    package_data={"flaskcbv": ["py.typed"]},
    include_package_data=True,
    distclass=BinaryDistribution,
    python_requires='>=3.8',
)
