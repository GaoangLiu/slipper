import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dofast",
    version="0.0.1b3",
    author="Gaogle",
    author_email="byteleap@gmail.com",
    description="A package for dirty faster Python programming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/slipper",
    package_dir={'': 'src'},
    py_modules=['dofast', 'argparse_helper', 'simple_parser'],
    # packages=setuptools.find_packages(),
    install_requires=[
        'colorlog>=4.6.1', 'tqdm>=4.56.0', 'PyGithub>=1.53', 'oss2>=2.0.2',
        'smart-open>=2.0'
    ],
    entry_points={
        'console_scripts': ['sli=argparse_helper:parse_arguments'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
