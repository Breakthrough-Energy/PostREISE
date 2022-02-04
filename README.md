![logo](https://raw.githubusercontent.com/Breakthrough-Energy/docs/master/source/_static/img/BE_Sciences_RGB_Horizontal_Color.svg)
[![PyPI](https://img.shields.io/pypi/v/postreise?color=purple)](https://pypi.org/project/postreise/)
[![codecov](https://codecov.io/gh/Breakthrough-Energy/PostREISE/branch/develop/graph/badge.svg?token=UFZ9CW4GND)](https://codecov.io/gh/Breakthrough-Energy/PostREISE)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Tests](https://github.com/Breakthrough-Energy/PostREISE/workflows/Pytest/badge.svg)
[![Documentation](https://github.com/Breakthrough-Energy/docs/actions/workflows/publish.yml/badge.svg)](https://breakthrough-energy.github.io/docs/)
![GitHub contributors](https://img.shields.io/github/contributors/Breakthrough-Energy/PostREISE?logo=GitHub)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Breakthrough-Energy/PostREISE?logo=GitHub)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/Breakthrough-Energy/PostREISE/develop?logo=GitHub)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Breakthrough-Energy/PostREISE?logo=GitHub)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code of Conduct](https://img.shields.io/badge/code%20of-conduct-ff69b4.svg?style=flat)](https://breakthrough-energy.github.io/docs/communication/code_of_conduct.html)


# PostREISE
**PostREISE** is part of a Python software ecosystem developed by [Breakthrough
Energy Sciences](https://science.breakthroughenergy.org/) to carry out power flow study
in the U.S. electrical grid.


## Main Features
Here are a few things that **PostREISE** can do:
* Perform transmission congestion/utilization analyses of scenarios
* Study generation/emission in scenarios
* Plot results of analyses

A detailed tutorial can be found on our [docs].


## Where to get it
* Clone or Fork the source code on [GitHub](https://github.com/Breakthrough-Energy/PostREISE)
* Get latest release from PyPi: `pip install postreise`


## Dependencies
**PostREISE** relies on:
* **PowerSimData**, another package developed by Breakthrough Energy Sciences and
available [here][PowerSimData]. You must have **PowerSimData** cloned in a folder
adjacent to your clone of **PostREISE** as the installation of packages depends on
files in **PowerSimData**.
* Several Python packages all available on [PyPi](https://pypi.org/) whose list can be
found in the ***requirements.txt*** or ***Pipfile*** files both located at the root of
this package.


## Installation
Scenario data managed by **PowerSimData** are used by the analysis and plotting modules
of **PostREISE**. Follow the instructions in the README of the [PowerSimData] package to install our
software ecosystem.


## License
[MIT](LICENSE)


## Documentation
[Code documentation][docstrings] in form of Python docstrings along with an overview of
the [package][docs] are available on our [website][website].


## Communication Channels
[Sign up](https://science.breakthroughenergy.org/#get-updates) to our email list and
our Slack workspace to get in touch with us.


## Contributing
All contributions (bug report, documentation, feature development, etc.) are welcome. An
overview on how to contribute to this project can be found in our [Contribution
Guide](https://breakthrough-energy.github.io/docs/dev/contribution_guide.html).



[docs]: https://breakthrough-energy.github.io/docs/postreise/index.html
[docstrings]: https://breakthrough-energy.github.io/docs/postreise.html
[website]: https://breakthrough-energy.github.io/docs/
[PowerSimData]: https://github.com/Breakthrough-Energy/PowerSimData
