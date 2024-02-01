from setuptools import setup, find_packages
from gpaslocal import __version__

setup(
    name='gpaslocal',
    version=__version__,
    description='Upload and manage GPAS data locally',
    author='Marc Brouard',
    author_email='brouard.marc@gmail.com',
    url="https://github.com/oxfordmmm/gpas_local_db",
    packages=find_packages(),
    install_requires=[
        "iso3166",
        "psycopg2-binary",
        "python-dotenv",
        "SQLAlchemy",
        "typing_extensions",
        "pydantic",
        "pandas",
        "openpyxl",
        "pyarrow",
        "errorhandler",
        "click",
        "click-log",
    ],
    extras_require={
        "dev": [
            "pytest",
            "alembic",
            "ipython",
            "mypy",
            "ruff",
        ]
    },
    entry_points={
        'console_scripts': [
            'gpaslocal = gpaslocal.cli:cli',
        ],
    },
    tests_require=["pytest"],
    python_requires='>=3.11',
)