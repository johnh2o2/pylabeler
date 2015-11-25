#!/usr/bin/env python

from distutils.core import setup

setup(name='pylabeler',
      version='1.0',
      description='Fast labeling/classification by hand',
      author='John Hoffman',
      author_email='jah5@princeton.edu',
      url='https://github.com/johnh2o2/pylabeler',
      package_dir = {'pylabeler': '.'},
      packages=['pylabeler'],
      requires=['matplotlib', 'numpy'],
      provides=['pylabeler']
     )
