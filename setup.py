import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dofast",
    version="0.1.1",  # Latest version .
    author="SLP",
    author_email="byteleap@gmail.com",
    description="A package for dirty faster Python programming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/slipper",
    packages=setuptools.find_packages(),
    package_data={"dofast":["dofast.json.zip", 'data/vps_init.sh']},
    install_requires=[
        'colorlog>=4.6.1', 'tqdm', 'PyGithub', 'oss2', 'lxml',
        'cos-python-sdk-v5', 
        'smart-open', 'pillow', 'bs4', 'arrow', 'numpy',
        'termcolor', 'codefast', 'python-twitter', 
	'deprecation'
    ],
    entry_points={
        'console_scripts': ['sli=dofast.sli_entry:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
