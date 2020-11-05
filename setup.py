import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='casex_alc',
      version='1.1',
      description='Casulty expection toolbox (alpha version)',
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
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
      zip_safe=False)
