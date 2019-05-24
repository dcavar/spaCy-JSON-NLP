
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spacyjsonnlp",
    version='0.0.13',
    python_requires='>=3.6',
    author="Damir Cavar, Oren Baldinger, Maanvitha Gongalla, Anurag Kumar, Murali Kammili",
    author_email="damir@cavar.me",
    description="The Python spaCy JSON-NLP package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dcavar/spaCy-JSON-NLP",
    packages=setuptools.find_packages(),
    install_requires=[
        'spacy>=2.1',
        'neuralcoref>=4.0',
        'pyjsonnlp>=0.2.12',
        'benepar[cpu]>=0.1.2',
        'cython',
        'numpy>=1.14'
    ],
    setup_requires=["cython", "numpy>=1.14", "pytest-runner"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    test_suite="tests",
    tests_require=["pytest", "coverage"]
)
