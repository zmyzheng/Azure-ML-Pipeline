import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aml-pipeline", 
    version="0.0.1",
    author="Mingyang Zheng",
    author_email="zhengzmy@gmail.com",
    description="Azure Machine Learning Pipeline high level API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zmyzheng/Azure-ML-Pipeline",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["azure-mgmt-resource==10.2.0", "pyjwt==1.7.1", "azureml-sdk==1.12.0"],
)
