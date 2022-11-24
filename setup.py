from setuptools import find_packages, setup

setup(
    name='anchormake',
    packages=find_packages(include=['anchormake']),
    version='0.1.0',
    description='Library for working with AnkerMake M5 FDM 3D Printers',
    author='Chad Fawcett',
    author_email='chad@useless.net',
    url='https://github.com/entropi/anchormake',
    license='MIT',
    python_requires='>=3.6',
    install_requires=['cryptography', 'paho-mqtt'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
