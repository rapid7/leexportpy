from setuptools import setup, find_packages
import leexportpy
setup(
    name='leexportpy',
    version=leexportpy.__version__,
    author='Safa Topal',
    author_email='Safa_Topal@rapid7.com',
    packages=find_packages(exclude=['*tests*']),
    url='https://github.com/logentries/leexportpy',
    license='MIT',
    description='Logentries by Rapid7 log export proxy for external systems.',
    long_description=open('README.md').read(),
    install_requires=['requests==2.9.1', 'datetime==4.1.1', 'daemonize==2.4.6',
                      'configobj==5.0.6', 'twisted==16.2.0', 'kafka==1.2.2'],
    entry_points={'console_scripts': ['leexportpy = leexportpy.leexport:main']},
    zip_safe=False
)
