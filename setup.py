from distutils.core import setup


# Setup for distutils.
setup(name='minfx',
      version='trunk',
      description='The minfx optimisation library',
      author="Edward d'Auvergne",
      author_email='edward@nmr-relax.com',
      url='https://gna.org/projects/minfx/',
      license='GPL',
      packages=['minfx', 'minfx.line_search', 'minfx.hessian_mods'])
