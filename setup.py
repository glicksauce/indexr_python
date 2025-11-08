import setuptools

setuptools.setup(
  name="indexr",        # your choice, but usually same as the package 
  version="0.1.0",          # obligatory
  install_requires=[
      "PySimpleGUI>=5.0.6",
      "coloredlogs>=15.0.1",
      "PyYaml>=6.0.3",
      "xattr>=1.3.0"
      ],
  entry_points={
        'console_scripts': [
            'main = indexr.main:main',
        ],
    },
)