"""
sentinel package installation
Create console entrypoint "sentinel" to execute sentinel commands
"""
from setuptools import setup, find_packages


setup(
    name='sentinel',
    version='2.0.3',
    description='Python project to register container docker as service in a backend',
    author='Ophélie Mauger, Etienne de Longeaux',
    author_email='ophelie.mauger@alterway.fr, etienne.de-longeaux@alterway.fr',
    entry_points={
        'console_scripts': ['sentinel=discovery.main:main']
    },
    packages=find_packages(where='.'),
    install_requires=[
        "docker==3.6.*",
        "requests==2.20.*",
        "python-consul==1.1.0",
        "jinja2>=2.10.1",
        "zope.interface==4.5.*",
        "ddd-domain-driven-design==0.0.2"
    ],
    extras_require={
        'ci': ['mock', 'pyinspector'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
)
