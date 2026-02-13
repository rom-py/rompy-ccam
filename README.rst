==========
rompy-ccam
==========


.. image:: https://img.shields.io/pypi/v/rompy_ccam.svg
        :target: https://pypi.python.org/pypi/rompy_ccam

.. image:: https://img.shields.io/travis/rom-py/rompy_ccam.svg
        :target: https://travis-ci.com/rom-py/rompy_ccam

.. image:: https://readthedocs.org/projects/rompy-ccam/badge/?version=latest
        :target: https://rompy-ccam.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Rompy CCAM Config package.


* Free software: Apache Software License 2.0
* Documentation: https://rompy-ccam.readthedocs.io.

Notice
------

**This is a work in progress! It is not yet usable!**

Features
--------

* TODO



Code Formatting and Pre-commit Hooks
------------------------------------

This repository enforces Python code formatting using [black](https://github.com/psf/black) via the pre-commit framework.

To set up pre-commit hooks locally (required for all contributors)::

    pip install pre-commit
    pre-commit install

This will automatically check code formatting before each commit. To format your code manually, run::

    pre-commit run --all-files

All code must pass black formatting before it can be committed or merged.

Versioning and Release
----------------------

This project uses [tbump](https://github.com/dmerejkowsky/tbump) for version management.

To bump the version, run::

    tbump <new_version>

This will update the version in `src/rompy_ccam/__init__.py`, commit the change, and optionally create a git tag.

tbump is included in the development requirements (`requirements_dev.txt`).

For more advanced configuration, see `tbump.toml` in the project root.
