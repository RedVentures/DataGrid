from glob import glob
from doctest import testmod
from sys import modules

import figleaf


files = glob('datagrid/*.py') + glob('datagrid/*/*.py')

figleaf.start()

for f in files:
    name = f.replace('.py','').replace('/','.')
    __import__(name)
    testmod(modules[name])

import tests.runner

figleaf.stop()
figleaf.write_coverage('.figleaf')
