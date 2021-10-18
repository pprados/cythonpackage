"""
   Copyright 2021 Philippe PRADOS

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import importlib
import sys
from pathlib import Path
from typing import List, Union, Tuple, Optional

from Cython.Build import cythonize
from setuptools import Extension
from setuptools.command.build_py import build_py as original_build_py


def _compile_package(package_path: Union[str, Path]) -> List[Extension]:
    package_path = str(package_path).replace('.', '/')  # FIXME
    sourcefiles = [str(path) for path in Path(package_path).rglob('*.pyx')]
    sourcefiles += [str(path) for path in Path(package_path).rglob('*.py')
                    if path.name not in ["__init__.py", "__compile__.py"]]
    sourcefiles.append(package_path + "/__compile__.py")
    # print(f'Extension(name="{package_path}.__compile__", sources={sourcefiles})')
    if not sourcefiles:
        return []
    return [Extension(
        name=f"{package_path}.__compile__",
        sources=sourcefiles,
    )]


def _compile_packages(packages: List[str]) -> List[Extension]:
    extensions: List[Extension] = []
    for package in packages:
        root = Path(package, "__compile__.py")
        if root.exists():
            extensions += _compile_package(root.parent)
    return extensions


# Chooses the right init function
class _CythonPackageMetaPathFinder(importlib.abc.MetaPathFinder):
    def __init__(self, name_filter: str, file: str):
        super(_CythonPackageMetaPathFinder, self).__init__()
        self._name_filter = name_filter
        self._file = file

    def find_module(self, fullname: str, path: str) -> Optional[importlib.machinery.ExtensionFileLoader]:
        if fullname.startswith(self._name_filter):
            # use this extension-file but PyInit-function of another module:
            return importlib.machinery.ExtensionFileLoader(fullname, self._file)


_compile_pyc = [False]
_optimize = 2
class _build_py(original_build_py):
    """ build_py to remove the source file for compiled package """

    def finalize_options(self):
        super().finalize_options()
        self.compile=_compile_pyc[0]
        self.optimize=_optimize

    def find_package_modules(self, package: str, package_dir: str) -> List[Tuple[str, str, str]]:
        modules: List[Tuple[str, str, str]] = super().find_package_modules(package, package_dir)
        filtered_modules = []
        for (pkg, mod, filepath) in modules:
            _path = Path(filepath)
            if (_path.suffix in [".py", ".pyx"] and
                    "__init__.py" != _path.name and
                    Path(_path.parent, "__compile__.py").exists()):  # FIXME: vérifier dans les sous packages
                continue
            filtered_modules.append((pkg, mod, filepath,))
        return filtered_modules

    def find_data_files(self, package, src_dir):
        """Return filenames for package's data files in 'src_dir'"""
        # Remove the source code via the data_files
        filtered_datas: List[str] = []
        for f in super().find_data_files(package, src_dir):
            _path = Path(f)
            if (_path.suffix in [".c", ".py", ".pyx"] and
                    "__init__.py" != _path.name and
                    Path(_path.parent, "__compile__.py").exists()):  # FIXME: vérifier dans les sous packages
                continue
            filtered_datas.append(f)
        return filtered_datas


# TODO: injection auto dans __init__
# Parametrage fin pour désactiver
# Article presse FR
# Article US
# Installation locale avec build_ext
# Verifier ok avec les sources en whl
# Cache des prefix à tester et supprimer les suffixes
# voir la gesion multi os https://github.com/pypa/cibuildwheel
def cythonpackage(dist, attr, value):
    """ Plugin for setuptools """
    if not value:
        return
    if isinstance(value, dict):
        inject_ext_modules = value.get("inject_ext_modules", True)
        remove_source = value.get("remove_source", True)
        compile_pyc = value.get("compile_pyc", "true").lower() in ['true', '1', 'yes']
        inject_init = value.get("inject_init", True)  # FIXME
    else:
        inject_ext_modules = True
        remove_source = True
        compile_pyc = True
        inject_init = True

    _compile_pyc[0] = compile_pyc

    compiled_module = cythonize(_compile_packages(dist.packages),
                                compiler_directives={'language_level': 3},
                                build_dir="build/cythonpackage"
                                )
    if dist.ext_modules:
        dist.ext_modules.extend(compiled_module)
    else:
        dist.ext_modules = compiled_module

    # Extend the build process to remove the compiled source code
    dist.cmdclass['build_py'] = _build_py


def init(module_name: str) -> None:
    """ Load the compiled module, and invoke the PyInit-function of another module """
    module = importlib.import_module(module_name + '.__compile__')
    sys.meta_path.append(_CythonPackageMetaPathFinder(module.__name__.split('.', 1)[0] + ".", module.__file__))
