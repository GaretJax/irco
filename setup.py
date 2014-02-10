#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages


class Setup(object):
    @staticmethod
    def read(fname, fail_silently=False):
        """
        Utility function to read the content of the given file.
        """
        try:
            return open(os.path.join(os.path.dirname(__file__), fname)).read()
        except:
            if not fail_silently:
                raise
            return ''

    @staticmethod
    def requirements(fname):
        """
        Utility function to create a list of requirements from the output of
        the pip freeze command saved in a text file.
        """
        packages = Setup.read(fname, fail_silently=True).split('\n')
        packages = (p.strip() for p in packages)
        packages = (p for p in packages if p and not p.startswith('#'))
        return list(packages)

    @staticmethod
    def get_files(*bases):
        """
        Utility function to list all files in a data directory.
        """
        for base in bases:
            basedir, _ = base.split('.', 1)
            base = os.path.join(os.path.dirname(__file__), *base.split('.'))

            rem = len(os.path.dirname(base)) + len(basedir) + 2

            for root, dirs, files in os.walk(base):
                for name in files:
                    yield os.path.join(basedir, root, name)[rem:]

    @staticmethod
    def version():
        data = Setup.read(os.path.join('irco', '__init__.py'))
        version = (re.search(u"__version__\s*=\s*u?'([^']+)'", data)
                   .group(1).strip())
        return version

    @staticmethod
    def test_links():
        # Test if hardlinks work. This is a workaround until
        # http://bugs.python.org/issue8876 is solved
        if hasattr(os, 'link'):
            tempfile = __file__ + '.tmp'
            try:
                os.link(__file__, tempfile)
            except OSError as e:
                if e.errno == 1:  # Operation not permitted
                    del os.link
                else:
                    raise
            finally:
                if os.path.exists(tempfile):
                    os.remove(tempfile)


Setup.test_links()

setup(name='irco',
      version=Setup.version(),
      description='International Research Collaboration Graphs',
      author='Jonathan Stoppani',
      author_email='jonathan@stoppani.name',
      url='https://github.com/GaretJax/irco',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=Setup.requirements('requirements.txt'),
      entry_points=Setup.read('entry-points.ini', True),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ])
