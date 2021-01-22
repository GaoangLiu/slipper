import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="slipper",
  version="0.0.3",
  author="Gaogle",
  author_email="byteleap@gmail.com",
  description="A small personal package",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/GaoangLiu/work",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)