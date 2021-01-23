import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="slipper",
  version="0.0.4",
  author="Gaogle",
  author_email="byteleap@gmail.com",
  description="A personal package for faster Python programming",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/GaoangLiu/slipper",
  packages=setuptools.find_packages(),
  install_requires=[
          'colorlog',
  ],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
)