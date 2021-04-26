from setuptools import find_packages, setup

setup(
    name="postreise",
    version="0.4",
    description="Extract, analyze and plot data from scenario",
    url="https://github.com/Breakthrough-Energy/PostREISE",
    author="Kaspar Mueller",
    author_email="kaspar@breakthroughenergy.org",
    packages=find_packages(),
    package_data={"postreise": ["data/*.csv"]},
    zip_safe=False,
)
