import setuptools

setuptools.setup(
    name="py_sass",
    version="0.0.57",
    author="Dumeni Manatschal",
    author_email="dumenim@ethz.ch",
    description=(" ... "),
    long_description="This module contains SM_SASS and ability to load SASS_Enc_Dom. Fixed UniformPredicate.",
    long_description_content_type="text/markdown",
    url="",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    install_requires=["termcolor", "py_sass_ext>=0.0.1", "psutil", "requests", "tabulate"],
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "py_sass_install_all = py_sass.install_finalize:main",
            "py_sass_install_finalize_only = py_sass.install_finalize:main_finalize_only"
        ]
    },
    cmdclass={}
)
