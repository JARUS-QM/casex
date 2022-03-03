import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='casex',
    version='1.0.7',
    description='Casualty expectation toolbox',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
    author='Anders la Cour-Harbo et al',
    author_email='anders@lacourfamily.dk',
    license='CC-BY-4.0',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    zip_safe=False,
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'descartes',
        'shapely'
    ]
)
