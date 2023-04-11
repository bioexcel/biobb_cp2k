import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_cp2k",
    version="4.0.0",
    author="Biobb developers",
    author_email="adam.hospital@irbbarcelona.org",
    description="Biobb_cp2k is a BioBB category for CP2K QM package.",
    long_description="Biobb_cp2k allows setup and simulation of QM simulations using CP2K QM package.",
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility QM CP2K",
    url="https://github.com/bioexcel/biobb_cp2k",
    project_urls={
        "Documentation": "http://biobb_cp2k.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/"
    },
    packages=setuptools.find_packages(exclude=['docs', 'test']),
    include_package_data=True,
    install_requires=['biobb_common==4.0.0'],
    python_requires='>=3.7,<3.10',
    entry_points={
        "console_scripts": [
            "cp2k_run = biobb_cp2k.cp2k.cp2k_run:main",
            "cp2k_prep = biobb_cp2k.cp2k.cp2k_prep:main"
        ]
    },
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
    ),
)
