from setuptools import setup, find_packages

setup(name='clean_folder',
      version='0.0.11',
      description='sorts files in folder by type',
      license='MIT',
      entry_points={'console_scripts':['clean-folder=clean_folder.clean:main']},
      packages=find_packages(),
      zip_safe=False)