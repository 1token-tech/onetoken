from setuptools import setup, find_packages

setup(name='btp',
      author='QbTrade',
      url='https://github.com/qbtrade/btp',
      author_email='markx914@gmail.com',
      packages=find_packages(),
      version='0.1',
      install_requires=[
          'requests',
          'pandas',
          'arrow',
          'PyJWT',
          'PyYAML',
          'aiohttp',
      ],
      zip_safe=False,
      )
