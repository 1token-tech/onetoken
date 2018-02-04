from setuptools import setup, find_packages

setup(name='onetoken',
      author='QbTrade',
      url='https://github.com/qbtrade/onetoken',
      author_email='markx914@gmail.com',
      packages=find_packages(),
      version='0.1.3',
      description='OneToken Trade System Python SDK',
      install_requires=[
          'arrow',
          'PyJWT',
          'PyYAML',
          'aiohttp',
      ],
      zip_safe=False,
      )
