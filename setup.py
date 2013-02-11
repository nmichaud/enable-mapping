# All rights reserved.
from os.path import join
from setuptools import setup, find_packages


info = {}
execfile(join('mapping', '__init__.py'), info)


setup(
    name = 'mapping',
    version = info['__version__'],
    author = 'Enthought, Inc.',
    author_email = 'info@enthought.com',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    #url = 'https://github.com/enthought/enable-mapping',
    #download_url = ('http://www.enthought.com/repo/ets/enable-mapping-%s.tar.gz' %
    #                info['__version__']),
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0], 
    description = 'application tools',
    long_description = open('README.rst').read(),
    include_package_data = True,
    package_data = {
        'mapping.enable': ['fonts/*']
    },
    install_requires = info['__requires__'],
    license = 'BSD',
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = True,
)
