from setuptools import setup, find_packages
from paip import __version__, software_name


dependencies = [
    'docopt',
    'luigi',
    'termcolor',
    'inflect',
    'sqlalchemy',
    'pymysql',
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn',
    'pyvcf',
]

setup(name=software_name,
      version=__version__,
      description='Medical Reports Pipeline from fastq files',
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
