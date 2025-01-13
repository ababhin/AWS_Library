# setup.py
import setuptools

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-ec2-lib",  # Replace with your desired package name
    version="0.1.0",
    author="Abhinav Bijpuria",
    author_email="abhinavbijpuria@gmail.com",
    description="A Python library to create, stop, and terminate EC2 instances with minimal input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aws-ec2-lib",  # Replace with your repository URL if available
    packages=setuptools.find_packages(),
    install_requires=[
        "boto3>=1.26.0",  # Ensure boto3 is installed
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",   # Or your chosen license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Specify your supported Python versions
)
