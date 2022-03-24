> Compile automatically pythons package in one shared library and remove the source code
when we build a distribution.

# Introduction
- Cython can compile a module but not a package ( a collection of modules )
- Sometime, you want to publish an optimized version of your python package/module.
- Sometime, you don't want to publish the source code.
You can use [PyArmor](https://pyarmor.readthedocs.io/en/latest/),
or [Pyminifier](https://liftoff.github.io/pyminifier/)
but if you want to compile the API, it's not a good approach.

## Using cython
Cython is complex for the *normal* python developer.
- To compile the code, you must use a `.pyx` file. It's break your simple usage : edit, test, edit, test.
Now, you must use : edit, **package**, test, edit, **package**, test.
- Cython propose to create a shared library for each *module*. If in you package, you have ten python file, you will
have ten shared library.
- The wheel package merge the python source code and the shared library. 
It's big and not confidential.

**We can do better.**

Based of the idea presented [here](https://newbedev.com/collapse-multiple-submodules-to-one-cython-extension), 
this component can help you to continue to use a classical python source code, 
and generate a single optimized module when you create the wheel.

And, it's VERY SIMPLE to use !

# Usage
For each package where you want to compile and/or hide the source code, 
**add a file `__compile__.py` with nothing**.
With that, you can continue to use your classical python file (or add some `.pyx` files).
For the developer point of vue, you continue to use the *interpreted* python code.

Then, to be compatible with [PEP-0517](https://www.python.org/dev/peps/pep-0517/),
- in the `pyproject.toml`
```
[build-system]
requires = ["setuptools>=42", "wheel", "cythonpackage[build]"]
build-backend = "setuptools.build_meta"
```

- in the `setup.py`:
```python
from setuptools import setup, find_packages

setup(
    setup_requires=['cythonpackage[build]'],
    cythonpackage=True,
    ...
    packages=find_packages(),
)
``` 
- in the `setup.cfg`, add other projects information:
```
[metadata]
name = my_compiled_project
...
```
Now, you can build your *compiled* wheel.
```shell
python3 -m pip install --upgrade build
python -m build
```
You can check inside the `dist/*.whl` to see if the source code in `__compile__` package are removed 
and replaced with a shared library. All others `.py` were pre-compiled.

In another virtualenv **and directory**, try to install this wheel.
```python
$ mkdir -p tmp
$ cd tmp
$ virtualenv test
$ source test/bin/activate
$ pip install ../dist/*.whl
$ python ...  # use your package
```
We use another virtualenv and another directory to remove the confusion between your local python source code
and the compiled version. Sometime, you use the *interpreted* version
if the source code are accessible with the `PYTHONPATH`.

You can check the running context with:
```python
if cython.compiled:
    print("Use compiled version")
else:
    print("Use slow interpreted version")
```

Use can try the sample present [here](https://github.com/pprados/test-cythonpackage): https://github.com/pprados/test-cythonpackage
Try to rename the `pyproject.toml` or `setup.py` to test different kind of builds.

## Multiple architecture
The wheel file generated is specific for an architecture and a Python version. 
The name describe that : `test_cythonpackage-0.0.0-cp38-cp38-manylinux_2_31_x86_64.whl`
To be compatible with multiple combinaison of python version or architecture, 
you must build wheels for all architecture. 
Try [cibuildwheel](https://cibuildwheel.readthedocs.io/en/stable/)
to generate a version of each Operating System and python versions.
```shell
$ pip install cibuildwheel
$ python3 -m cibuildwheel --output-dir dist --platform linux
```

To create a *classical* version of your package, without compilation and with source code, use:
```shell
$ CYTHONPACKAGE=false python3 -m setup.py bdist_wheel
```


Use a CI action like github action. You can generate something like:
```
test_cythonpackage-0.0.0-cp37-cp37m-macosx_10_15_x86_64.whl
test_cythonpackage-0.0.0-cp37-cp37m-manylinux_2_12_i686.manylinux_2_5_i686.manylinux1_i686.manylinux2010_i686.whl
test_cythonpackage-0.0.0-cp37-cp37m-manylinux_2_12_x86_64.manylinux_2_5_x86_64.manylinux1_x86_64.manylinux2010_x86_64.whl
test_cythonpackage-0.0.0-cp37-cp37m-musllinux_1_1_i686.whl
test_cythonpackage-0.0.0-cp37-cp37m-musllinux_1_1_x86_64.whl
test_cythonpackage-0.0.0-cp37-cp37m-win32.whl
test_cythonpackage-0.0.0-cp37-cp37m-win_amd64.whl
test_cythonpackage-0.0.0-cp38-cp38-macosx_10_15_x86_64.whl
test_cythonpackage-0.0.0-cp38-cp38-manylinux_2_12_i686.manylinux_2_5_i686.manylinux1_i686.manylinux2010_i686.whl
test_cythonpackage-0.0.0-cp38-cp38-manylinux_2_12_x86_64.manylinux_2_5_x86_64.manylinux1_x86_64.manylinux2010_x86_64.whl
test_cythonpackage-0.0.0-cp38-cp38-musllinux_1_1_i686.whl
test_cythonpackage-0.0.0-cp38-cp38-musllinux_1_1_x86_64.whl
test_cythonpackage-0.0.0-cp38-cp38-win32.whl
test_cythonpackage-0.0.0-cp38-cp38-win_amd64.whl
test_cythonpackage-0.0.0-cp39-cp39-macosx_10_15_x86_64.whl
test_cythonpackage-0.0.0-cp39-cp39-manylinux_2_12_i686.manylinux_2_5_i686.manylinux1_i686.manylinux2010_i686.whl
test_cythonpackage-0.0.0-cp39-cp39-manylinux_2_12_x86_64.manylinux_2_5_x86_64.manylinux1_x86_64.manylinux2010_x86_64.whl
test_cythonpackage-0.0.0-cp39-cp39-musllinux_1_1_i686.whl
test_cythonpackage-0.0.0-cp39-cp39-musllinux_1_1_x86_64.whl
test_cythonpackage-0.0.0-cp39-cp39-win32.whl
test_cythonpackage-0.0.0-cp39-cp39-win_amd64.whl
test_cythonpackage-0.0.0-pp37-pypy37_pp73-macosx_10_15_x86_64.whl
test_cythonpackage-0.0.0-pp37-pypy37_pp73-manylinux_2_12_i686.manylinux_2_5_i686.manylinux1_i686.manylinux2010_i686.whl
test_cythonpackage-0.0.0-pp37-pypy37_pp73-manylinux_2_12_x86_64.manylinux_2_5_x86_64.manylinux1_x86_64.manylinux2010_x86_64.whl
```
and add a fallback with a classical version with source code.
```
test_cythonpackage-0.0.0-py3-none-any.whl
```
The [PIP-0425](https://www.python.org/dev/peps/pep-0425/) explain how the best package are selected.

## Using standard PEP-517
Don't forget to add a file `__compile__.py` with nothing in package to compile.

With classical setuptools, 
- in `pyproject.toml`
```
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
```
- in `setup.py`
```python
from setuptools import setup, find_packages

setup(
    setup_requires=['cythonpackage[build]'],
    cythonpackage=True,
    packages=find_packages(),
)
``` 
- in the `setup.cfg`, add other projects information:
```
[metadata]
name = my_compiled_project
...
and
```shell
$ pip wheel --use-pep517 .
```

## Using Poetry
Poetry propose a new approach to build a *wheel*, compatible with PEP 517.
At this time, the last version (1.1.*) is not compatible with *cython*
and it's not possible to add a plugin with enough features, 
but you can use it in a more complex approach:

Don't forget to add a file `__compile__.py` with nothing in package to compiled.

Create a `pyproject.toml` file with something like this:
```toml
[build-system]
build-backend = "poetry.core.masonry.api"
requires = ["cythonpackage[poetry]"]

[tool.poetry]
name = "test"
version = "0.0.0"
description = "Test"
authors = ["Me <me@me.org>"]
packages = [
    { include = "foo" },
    { include = "foo2" },
    { include = "foo3" },
]
exclude = ["**/[!__]*.py"] # Remove source code
build = 'poetry_build.py'

[tool.poetry.dependencies]
python = "^3.7"
cythonpackage = "*"

[build-system]
requires = ["poetry-core>=1.2.0a2"]
build-backend = "poetry.core.masonry.api"
```
and a file `./poetry_build.py`:
```python
import cythonpackage
def build(setup_kw):
    cythonpackage.build_cythonpackage(setup_kw)
```
Then, you can build the package with:
```shell
python -m build -w
```
or
```shell
pip wheel -w dist .
```

## Using setup.py only ([obsolete](https://setuptools.pypa.io/en/latest/userguide/declarative_config.html))
Don't forget to add a file `__compile__.py` with nothing in package to compiled.

In the `setup.py`, add `setup_requires` and `cythonpackage=True`:

```python
from setuptools import setup, find_packages

setup(
    name="myname",
    version="v0.0.0",
    setup_requires=['cythonpackage[build]'],
    install_requires=['cythonpackage'],
    cythonpackage=True,
    packages=find_packages(),
)
```
Now, you can build your *compiled* wheel.
```shell
python setup.py bdist_wheel
```


## Using PBR ([obsolete](https://setuptools.pypa.io/en/latest/userguide/declarative_config.html))
[PBR](https://docs.openstack.org/pbr/latest/) is a library for managing 
setuptools packaging needs in a consistent manner.

Don't forget to add a file `__compile__.py` with nothing in package to compiled.

You can use use PBR with CythonPackage in `setup.cfg`:
```
[metadata]
name = my_compiled_project
setup_requires=cythonpackage,pbr
cythonpackage=True
pbr=True
...
[options]
install_requires =
    cythonpackage
```
or `setup.py`
```python
from setuptools import setup

setup(
    setup_requires=['pbr','cythonpackage[build]'],
    pbr=True,
    cythonpackage=True,
)
```
Now, you can build your *compiled* wheel.
```shell
python setup.py bdist_wheel
```

# Sample
The project [test-cythonpackage](https://github.com/pprados/test-cythonpackage) propose a tiny exemple
to use CythonPackage, and generate all binary version, 
with a [GitHub Action](https://docs.github.com/en/actions).

# Advanced usage
To make this magic, we manipulate some special parameters at different levels. 
You can remove some manipulation with a dictionary in `cythonpackage` parameter.
```python
from setuptools import setup, find_packages

setup(
    setup_requires=['pbr','cythonpackage'],
    pbr=True,
    cythonpackage={
        "inject_ext_modules": True,
        "inject_init": True,
        "remove_source": True,
        "compile_py": True,
        "optimize": 1,
        "exclude": []  # List of glob
    },
)
```

and you can de-activate CythonPackage with the environment variable `CYTHONPACKAGE=false`
```shell
CYTHONPACKAGE=false python setup.py bdist_wheel
```
to generate a *classical* version, without compilation and with python source code.

## inject_ext_modules
Detect all packages with `__compile__.py`, and generate a list of `Extension` to generate the compiled version of
the module `__compile__` with all the source code. But with this, it's important to add an extension in
`sys.meta_path` to use only one shared library.
It's done at the begining in all `__init__.py` files.

If you set this parameter to `False`, you must write yourself the `ext_modules` parameter
```python
setup(...
      ext_modules=cythonize(
        [
            Extension(
                    name=f"foo.__compile__",
                    sources=['foo/*.py']
                )
        ],
        build_dir="build/cythonpackage",
        compiler_directives={'language_level': 3}
      )
)
```

## inject_init
By default, during the build process, all the `__init__.py` file for the package with `__compile__.py` are patched
on the fly, to inject two line:
```python
import cythonpackage
cythonpackage.init(__name__)
```
If this manipulation break something, set this parameter to `False` and add yourself these two lines
at **THE BEGINNING** of the file, before others `import`.

## remove_source
Because the shared library is enough to use the package, the source code is not necessary. And, sometime, it's possible
to have a confusion between the *compiled* version and the *interpreted* version. To be sure to use the *compiled*
version, we remove all the source code of the compiled files.

If you set this parameter to `False`, the source code were inside the wheel.

## compile_py / optimize
The objectif of this kind of build, it to optimize the usage of the package. 
Normally, it's possible to compile the source code to python-byte-code 
with `python setup.py build_py --compile`. 
But the `bdist_wheel` can not receive the `--compile` parameter.

With CythonPackage, by default, the `compile` is set to `True`, 
and the `optimize` is set to `1` to remove the assertions.

You can change these parameters.

## exclude
Sometime, a specific python source code can not be compiled with Cython.
You can exclude this file with a list of glob pattern.
```python
setup(
    setup_requires=['pbr','cythonpackage'],
    pbr=True,
    cythonpackage={
        "exclude": ["foo/*special.py"]  # List of glob
    },
    install_requires = ["cythonpackage"]
)
```
