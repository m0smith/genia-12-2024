from setuptools import setup, find_packages

setup(
    name='genia',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'genia=genia_interpreter:GENIAInterpreter',
        ],
    },
    install_requires=[],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    description='GENIA - A concise scripting language interpreter for data processing and automation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/genia',
    license='MIT',
)
