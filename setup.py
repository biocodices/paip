from setuptools import setup, find_packages
from paip import __version__, software_name


dependencies = [
    'docopt',
    'luigi',
    'termcolor',
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
]

setup(name=software_name,
      version=__version__,
      description='Variant calling pipeline',
      url='http://github.com/biocodices/paip',
      author='Juan Manuel Berros',
      author_email='juanma.berros@gmail.com',
      install_requires=dependencies,
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
            'paip = paip.run_task:run_task'
          ]
      },
      zip_safe=False)
