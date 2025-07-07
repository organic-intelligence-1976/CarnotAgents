from setuptools import setup, find_packages

setup(
    name="renaissance",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "pandas",
        "jupyter",
    ],
    description="A flexible framework for iterative document-based problem solving through LLM interactions",
    author="Renaissance Team",
    author_email="example@example.com",
    url="https://github.com/example/renaissance",
)