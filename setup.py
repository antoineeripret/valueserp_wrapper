from setuptools import setup, find_packages

setup(
    name='valueserpwrapper',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'pandas==2.1.4', 
        'requests==2.31.0'
    ],
    # Additional metadata about your package.
    author='Antoine Eripret',
    author_email='antoine.eripret.dev@gmail.com',
    description='A simple wrapper for ValueSERP API',
    url='https://github.com/antoineeripret/valueserp_wrapper',
)