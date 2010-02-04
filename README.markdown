DataGrid
========
Tabular Data Rendering Library

This package is composed of two main components.  The library, which is the 
main purpose of this project, and an executable (rendergrid) that uses the 
library for shell-level access to the library.  There are also PHP bindings 
which utilize the rendergrid script for access to the datagrid from php.

Features
--------
Currently supported features:

*   Sorting
*   Grouping
*   Aggregation of data at group & totals levels
*   Calculated columns: Add new columns derived from raw data.
*   Column formatting 

Requirements
------------
Core DataGrid library and rendergrid exec:

*   Python 2.6+

PHP Bindings:

*   PHP 5.2+

Installation
------------
The installation process will install the library in python's site-packages 
dir, the rendergrid executable in your bin dir, and if you have php installed 
will attempt to install the php bindings in your php-path.

To install:
    python setup.py install

Usage (python library)
----------------------
Render of basic table with ascii renderer:

    >>> from datagrid.core import DataGrid
    >>> from datagrid.renderer.ascii import Renderer
    >>> grid = DataGrid([[1,2,3],[4,5,6]])
    >>> print grid.render(Renderer())
    A   B   C
    ============
    1   2   3
    4   5   6
    ============

Usage (rendergrid exec)
-----------------------
Render a csv file with headers:
    rendergrid -A myfile.csv

For more help with the rendergrid executable:
    rendergrid -h


