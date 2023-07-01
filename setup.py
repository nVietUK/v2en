from setuptools import find_packages, setup

setup(
    name="v2enlib",
    packages=find_packages(include=["v2enlib"]),
    version="0.0.1",
    description="library support for add data set to .db file and training base on those data",
    author="TakahashiNguyen",
    license="GNU GENERAL PUBLIC LICENSE v3",
    setup_requires=["pytest-runner"],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
)
