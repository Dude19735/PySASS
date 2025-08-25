import setuptools

setuptools.setup(
    name="py_cubin",
    version="0.0.14",
    author="Dumeni Manatschal",
    author_email="dumenim@ethz.ch",
    description=(" ... "),
    long_description="This module contains Py_Cubin decode server and smd tools.",
    long_description_content_type="text/markdown",
    url="",
    project_urls={},
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
    install_requires=["termcolor", "py_sass_ext>=0.0.1", "py_sass>=0.0.24"],
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "py_cubin_smd_service = py_cubin.sm_cubin_service:py_cubin_smd_service",
            "smd = py_cubin.sm_cubin_smd:py_smd",
        ]
    },
    cmdclass={}
)
