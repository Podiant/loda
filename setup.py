from setuptools import setup


entry_points = (
    '[console_scripts]\n'
    'loda=loda.cli:main'
)

setup(
    name='loda',
    version='0.1',
    py_modules=['loda'],
    install_requires=[
        'Click',
        'colorama',
        'dateparser',
        'Jinja2',
        'pyfiglet',
        'PyYAML',
        'requests',
        'termcolor'
    ],
    entry_points=entry_points
)
