from setuptools import setup

setup(name='postreise',
      version='0.1',
      description='Extract, analyze and plot data from scenario',
      url='https://github.com/intvenlab/PostREISE',
      author='Kaspar Mueller',
      author_email='kmueller@intven.com',
      packages=setuptools.find_packages(),
      package_data={'postreise':['extract/*.m']},
      zip_safe=False)
