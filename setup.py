from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='kenna',
    version='0.4.0',
    author='Tyler Fisher',
    author_email='tylerfisher@tylerfisher.ca',
    description="An API client for Kenna Security",
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Topic :: Security',
    ],
    packages=find_packages(),
    install_requires=[],
)
