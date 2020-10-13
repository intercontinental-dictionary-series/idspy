from setuptools import setup, find_packages


setup(
    name='idspy',
    version='0.2.1.dev0',
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    description='Python library providing shared code for IDS datasets',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='',
    license='Apache 2.0',
    url='https://github.com/intercontinental-dictionary-series/idspy',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    entry_points={
    # FIXME: provide a cldfbench scaffold!
    },
    platforms='any',
    python_requires='>=3.5',
    install_requires=[
        'clldutils',
        'pybtex<0.23; python_version < "3.6"',
        'pybtex; python_version > "3.5"',
        'pylexibank>=2.7.2',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=5',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
