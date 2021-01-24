import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xiu",
    version="0.0.1b1",
    author="Gaogle",
    author_email="byteleap@gmail.com",
    description="A personal package for faster Python programming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/slipper",
    package_dir={'': 'src'},
    py_modules=['xiu', 'logger'],
    # packages=setuptools.find_packages(),
    install_requires=['colorlog>=4.6.1', 'tqdm>=4.56.0'],
    entry_points={
        'console_scripts': ['sli=xiu:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
