from setuptools import setup, find_packages

setup(
    name='pytest-sequence-reporter',
    version='0.1.0',
    author='Mark Mayhew',
    author_email='mark.mayhew@javs.com',
    description='A Pytest plugin for reporting test events to a sequencer GUI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/JusticeAVSolutions/Pytest-Sequence-Reporter',
    packages=find_packages(),
    install_requires=[
        'pytest>=6.0.0',
        'requests',
        'pytest-json-report'
    ],
    entry_points={
        'pytest11': [
            'sequence_reporter = pytest_sequence_reporter.plugin',
        ],
    },
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python :: 3',
    ],
)
