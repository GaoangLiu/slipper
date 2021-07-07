import setuptools
import codefast as cf


setuptools.setup(
    name="dofast",
    version="0.4.2",  # Latest version .
    author="SLP",
    author_email="byteleap@gmail.com",
    description="A package for dirty faster Python programming",
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/slipper",
    packages=setuptools.find_packages(),
    package_data={
        "dofast": ["dofast.json.zip", 'data/vps_init.sh', 'data/*.txt']
    },
    install_requires=[
        'colorlog>=4.6.1', 'tqdm', 'PyGithub', 'oss2', 'lxml',
        'cos-python-sdk-v5', 'smart-open', 'pillow', 'bs4', 'arrow', 'numpy',
        'termcolor', 'codefast', 'python-twitter', 'deprecation', 'faker', 'pynsq'
    ],
    entry_points={
        'console_scripts': [
            'sli=dofast.sli_entry:main', 'hint=dofast.sli_entry:_hint_wubi',
            'snc=dofast.sli_entry:_sync', 'oss=dofast.sli_entry:secure_oss',
            'pxy=dofast.sli_entry:pxy', 'websurf=dofast.nsq.websurf:run',
            'weather=dofast.weather:entry','jsonify=dofast.sli_entry:jsonify'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
