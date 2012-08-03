# This should be only one line. If it must be multi-line, indent the second
# line onwards to keep the PKG-INFO file format intact.
"""Live system monitoring."""

from setuptools import setup, find_packages
import glob
import os.path

version = '0.1.dev0'

setup(
    name='livemonitor',
    version=version,
    install_requires=[
        'distribute',
        'flask',
        'gevent-websocket',
    ],
    entry_points="""
        [console_scripts]
            livemonitor = livemonitor.app:main
    """,
    author='Christian Theune <ct@gocept.com>',
    author_email='ct@gocept.com',
    license='BSD (2-clause)',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
