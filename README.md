When we build a wheel, compile some pythons package in one `.so` file and remove the source code. 

# Introduction
Sometime, you want to publish your module, but not the source code.
You can use [PyArmor](https://pyarmor.readthedocs.io/en/latest/), 
but if you want to keep the API, it's not a good approach.

Sometime, you want to compile your python code, but you don't want to manage the `.pyx` files.


Cython propose to create a shared library for each *module*. If in you package, you have ten python file, you will
have ten shared library.

We can do better.

Based of the idea presented [here](https://newbedev.com/collapse-multiple-submodules-to-one-cython-extension), this
module can help you to continue to use a classical python source code, and generate a single shared library when you
create the wheel.

# Usage
For each package, who you want to compile and hide the source code, add a file `__compile__.py` with nothing.
In the `__init__.py` of the package, at the very beginning of the file, add

```python
# __init__.py
import cythonpackage
cythonpackage.init(__name__)

# ... other import, __all__ = ...
```
With that, you can continue to use your classical python file, or add some `.pyx` files.

To finish, in the `setup.py`, add:

```python
from setuptools import setup, find_packages

setup(
    setup_requires=['cythonpackage'],
    cythonpackage=True,
    packages=find_packages(),
    requires=['cythonpackage'],
)
```
Now, you can build your wheel.
```shell
python setup.py bdist_wheel
```
You can unzip the `dist/*.whl`file to see if the source code in `__compile__` package are removed, 
and replaced with a `.so` file.

In another virtualenv, try to install this wheel.
```python
$ virtualenv test
$ source test/bin/activate
$ pip install dist/*.whl
$ python ...  # use your package
```
The wheel file is specific for an architecture. You must build de wheel for each architecture.

With [PBR](https://docs.openstack.org/pbr/latest/), use:
```python
from setuptools import setup, find_packages

setup(
    setup_requires=['pbr','cythonpackage'],
    pbr=True,
    cythonpackage=True,
)
```


TODO: https://python-poetry.org/
