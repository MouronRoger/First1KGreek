"""Setup configuration for First1KGreek Browser."""

from setuptools import setup, find_namespace_packages

setup(
    name="first1k",
    version="1.2.0",
    description="First1KGreek Browser - A tool for browsing Greek texts from the First Thousand Years Project",
    author="James",
    packages=find_namespace_packages(where="src", include=["first1k", "first1k.*"]),
    package_dir={"": "src"},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "first1k=first1k.__main__:main",
        ],
    },
    python_requires=">=3.6",
) 