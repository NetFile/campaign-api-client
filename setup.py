from setuptools import setup

setup(name='Campaign API Client',
      version='0.1',
      description='Campaign API Client Library',
      url='https://github.com/NetFile/campaign-api-client',
      author='Rob Krieg',
      author_email='krieg@netfile.com',
      license='MIT',
      packages=['campaign-api-client'],
      zip_safe=False, install_requires=['requests', 'psycopg2'])
