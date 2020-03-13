from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

# Thanks to @joelbarmettlerUZH on Medium

setup(
    name='pyion2json',
    packages=['pyion2json'],
    description='Convert an Amazon Ion document(s) to JSON',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.0.2',
    license='MIT',
    author='crouchcd',
    author_email='cdcsoftdev@gmail.com',
    url='https://github.com/crouchcd/pyion2json',
    download_url='https://github.com/crouchcd/pyion2json/archive/0.0.2.tar.gz',
    keywords=[
        'Amazon',
        'Ion',
        'JSON'
    ],
    install_requires=[
        'amazon.ion'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
)
