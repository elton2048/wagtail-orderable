from setuptools import setup, find_packages
import subprocess

INSTALL_REQUIRES = [
    "wagtail>=2.0,<3.0",
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Framework :: Django',
    'License :: OSI Approved :: zlib/libpng License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Framework :: Wagtail',
]


setup(
    name='wagtail-orderable',
    version='1.0.1',
    description='Orderable support for Wagtail',
    long_description="Provides drag-and-drop support ordering support to the ModelAdmin listing view.",
    author='Elton Lee & Andy Babic',
    author_email='elton2048@gmail.com',
    url='https://github.com/elton2048/wagtail-orderable',
    install_requires=INSTALL_REQUIRES,
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    classifiers=CLASSIFIERS,
)