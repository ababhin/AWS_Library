import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-services",  # Package name on PyPI or for installation
    version="0.1.0",
    author="Abhinav Bijpuria",
    author_email="abhinavbijpuria@gmail.com",
    description="A library for managing AWS services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ababhin/AWS_Library.git",  # Update with your repository URL
    packages=setuptools.find_packages(),  # Automatically find packages under 'aws_services'
    install_requires=[
        # List dependencies here, e.g.,
        "boto3>=1.34.0",
        # Add other dependencies as needed
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Change if using a different license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
