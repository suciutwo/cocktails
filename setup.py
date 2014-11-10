from distutils.core import setup
setup(name='cocktails',
      version='0.2',
      description='Cocktail Generation and Analysis',
      author='Emma Pierson and Andrew Suciu',
      author_email='suciu@cs.stanford.edu',
      url='https://github.com/suciutwo/cocktails/',
      packages=['src'],
      data_files=[('data', ['data/amount_parsing_map',
                            'data/cleaned_ingredients',
                            'data/cleaned_matrices',
                            'data/cleaned_recipes',
                            'data/saved_cocktails',
                            'data/saved_ingredients'])]
      )