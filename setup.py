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
        'Flask',
        'Werkzeug==2.0.0',
        #'Flask-WTF',
        #'Flask-SQLAlchemy',
    ],

    classifiers=[
        "Programming Language :: Python :: 3.8",
    ],

    include_package_data=True,
    distclass=BinaryDistribution,
    python_requires='>=3.6',
)
