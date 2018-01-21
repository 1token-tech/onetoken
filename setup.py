from setuptools import setup, find_packages

setup(name='ots',
      author='QbTrade',
      url='https://github.com/qbtrade/ots',
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
