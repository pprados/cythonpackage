When we build a wheel, compile automatically pythons package in one shared library and remove the source code. 

# Introduction
Sometime, you want to publish your module, but not the source code.
You can use [PyArmor](https://pyarmor.readthedocs.io/en/latest/), 
but if you want to keep the API, it's not a good approach.

## Using cython
Cython is complex for the *normal* python developer.
- To compile the code, you must use a `.pyx` file. It's break your simple usage : edit, test, edit, test.
Now, you must use : edit, **package**, test, edit, **package**, test.
- Cython propose to create a shared library for each *module*. If in you package, you have ten python file, you will
have ten shared library.
- The wheel package merge the python source code and the shared library

We can do better.

Based of the idea presented [here](https://newbedev.com/collapse-multiple-submodules-to-one-cython-extension), 
this component can help you to continue to use a classical python source code, 
and generate a single shared library when you create the wheel.

And, it's VERY SIMPLE to use !

# Usage
For each package, who you want to compile and/or hide the source code, add a file `__compile__.py` with nothing.
With that, you can continue to use your classical python file or add some `.pyx` files.
For the developer point of vue, you continue to use the *interpreted* python code.

Then, in the `setup.py`, add `setup_requires` and `cythonpackage=True`:

```python
from setuptools import setup, find_packages

setup(
    setup_requires=['cythonpackage'],
    cythonpackage=True,
    packages=find_packages(),
    requires=['cythonpackage'],
)
```
Now, you can build your *compiled* wheel.
```shell
python setup.py bdist_wheel
```
You can check inside the `dist/*.whl` to see if the source code in `__compile__` package are removed 
and replaced with a shared library. All others `.py` were pre-compiled.

In another virtualenv, try to install this wheel.
```python
$ virtualenv test
$ source test/bin/activate
$ pip install dist/*.whl
$ python ...  # use your package
```
We use another virtualenv to remove the confusion between your python source code
and the compiled version. Sometime, you use the *interpreted* version
it the source code is accessible with the `PYTHONPATH`.

## Multiple architecture
The wheel file is specific for an architecture and a Python version. 
You must build de wheel for each architecture. 
Try [cibuildwheel](https://cibuildwheel.readthedocs.io/en/stable/)
to generate a version of each Operating System.

## PBR
[PBR](https://docs.openstack.org/pbr/latest/) is a library for managing 
setuptools packaging needs in a consistent manner.

You can use use PBR with CythonPackage:
```python
from setuptools import setup, find_packages

setup(
    setup_requires=['pbr','cythonpackage'],
    pbr=True,
    cythonpackage=True,
)
```


# Advanced usage
To make this magie, we manipulate some parameters. You can remove some manipulation with a dict 
in `cythonpackage` parameter.
```python
from setuptools import setup, find_packages

setup(
    setup_requires=['pbr','cythonpackage'],
    pbr=True,
    cythonpackage={
        "inject_ext_modules": True,
        "inject_init": True,
        "remove_source": True,
        "compile_pyc": True,
        "optimize": 2,
    },
)
```
Note: the `install_requires` is automatically extended with `cythonpackage`.

## inject_ext_modules
Detect all package with `__compile__.py`, and generate a list of `Extension` to generate the compiled version of
the module `__compile__` with all the source code. But with this, it's important to add an extension in
`sys.meta_path` to use only one shared library.
It's done in the `__init__.py`

If you set this parameter to False, you must write yourself the `ext_modules` parameter
```python
setup(...
      ext_modules=cythonize(
        Extension(
                    name=f"foo.__compile__",
                    sources=["foo/bar_a.py","foo/bar_b.py"],
                ))
)
```

## inject_init
By default, during the build process, all the `__init__.py` file for the package with `__compile__.py` are patched
on the fly, to inject two line:
```python
import cythonpackage
cythonpackage.init(__name__)
```

## remove_source
Because the shared library is enough to use the package, the source code is not necessary. And, sometime, it's possible
to have a confusion between the *compiled* version and the *interpreted* version. To be sure to use the *compiled*
version, we remove all the source code of the compiled files.

If you set this parameter to False, the source code were in the whell.

## compile_pyc / optimize
The objectif of this kind of build, it to optimize the usage of the package. Normally, it's possible to compile
the source code with `python setup.py build_py --compile`. 
But the `bdist_wheel`can not receive the `--compile` parameter.
With CythonPackage, by default, the `compile` is set to True, and the `optimize` is set to `2`

You can change these parameters.


# TODO:
Check with TODO: https://python-poetry.org/
