from setuptools import setup, find_packages


long_description = open('README.md').read()

setup(
    name='pyipma',
    version='1.0.1',
    license='MIT License',
    url='https://github.com/dgomes/pyipma',
    author='Diogo Gomes',
    author_email='diogogomes@gmail.com',
    description='Python library to retrieve information from Instituto Português do Mar e Atmosfera.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['pyipma'],
    zip_safe=True,
    platforms='any',
    install_requires=list(val.strip() for val in open('requirements.txt')),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
