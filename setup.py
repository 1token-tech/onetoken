import re
from setuptools import setup, find_packages

with open('onetoken/__init__.py', 'r', encoding='utf8') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)
    print('regex find version', version)
if not version:
    raise RuntimeError('Cannot find version information')

setup(name='onetoken',
      author='QbTrade',
      url='https://github.com/qbtrade/onetoken',
      author_email='markx914@gmail.com',
      packages=find_packages(),
      version=version,
      description='OneToken Trade System Python SDK',
      install_requires=[
          'arrow',
          'PyJWT',
          'PyYAML',
          'aiohttp==2.3.10',
      ],
      zip_safe=False,
      )
