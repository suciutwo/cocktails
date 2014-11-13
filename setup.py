from setuptools import setup, find_packages
setup(name='cocktails',
      version='0.3',
      description='Cocktail Generation and Analysis',
      author='Emma Pierson and Andrew Suciu',
      author_email='suciu@cs.stanford.edu',
      url='https://github.com/suciutwo/cocktails/',
      packages= ['src', 'src.data_processing', 'src.data_visualization', 'data'],
      install_requires=['regex', 'enum34', 'numpy', 'pandas', 'scipy'],
      include_package_data=True
)