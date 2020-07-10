import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="gosnomer",
    version="0.0.2",
    author="Alexey Leshchenko",
    author_email="leshchenko@gmail.com",
    description="Исправление ручного ввода автомобильных номеров РФ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leshchenko1979/gosnomer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="MIT"
)