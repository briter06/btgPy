from setuptools import setup, find_packages



setup(
    name='CHAID',
    version=get_version(),
    description='A CHAID tree building algorithm',
    long_description="This package provides a python implementation of the Chi-Squared Automatic Inference Detection (CHAID) decision tree",
    url='https://github.com/bgonzalezd/btgPy',
    author='Briter Gonzalez',
    author_email='btg.developers@gmail.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='CHAID pandas numpy scipy statistics statistical analysis',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'cython',
        'numpy',
        'pandas',
        'treelib',
        'pytest',
        'scipy',
        'savReaderWriter',
        'graphviz',
        'plotly',
        'colorlover',
        'enum34; python_version == "2.7"'
    ],
    extras_require={
        'test': ['codecov', 'tox', 'tox-pyenv', 'detox', 'pytest', 'pytest-cov'],
    }
)
