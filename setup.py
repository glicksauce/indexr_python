import setuptools

setuptools.setup(
  name="indexr",        # your choice, but usually same as the package 
  version="0.1.0",          # obligatory
  install_requires=[],      # your dependencies, if you have any
  entry_points={
        'console_scripts': [
            'main = indexr.main:main',
        ],
    },
)