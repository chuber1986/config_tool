from setuptools import setup


setup(
    name='ConfigTool',
    author='Christian Huber',
    author_email='christian.huber@silicon-austria.com',
    maintainer='Christian Huber',
    maintainer_email='christian.huber@silicon-austria.com',
    version='1.0',
    packages=['config'],
    package_data={},
    include_package_data=True,
    install_requires=[],
    extras_require={},
    url='https://git.silicon-austria.com',
    download_url='https://git.silicon-austria.com/huberc/config_tool',
    license='BSD',
    description='Read configuration from file and update with argument values.',
    long_description=open('README.md').read(),
    python_requires='>=3.6',
    tests_require=["pytest>=3.6", "pytest-runner"],
    test_suite='tests'
)

