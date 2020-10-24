import setuptools

with open("README.md", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="eyekit",
    use_scm_version={
        "write_to": "eyekit/_version.py",
        "write_to_template": '__version__ = "{version}"',
        "fallback_version": "???",
    },
    author="Jon Carr",
    author_email="jcarr@sissa.it",
    description="A Python package for analyzing reading behavior using eyetracking data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://jwcarr.github.io/eyekit/",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.6",
    install_requires=["cairocffi>=1.1", "numpy>=1.19"],
    setup_requires=["setuptools_scm"],
)
