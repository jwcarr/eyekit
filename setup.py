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
    packages=["eyekit"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Text Processing :: Fonts",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=["cairocffi>=1.1"],
    setup_requires=["setuptools_scm"],
)
