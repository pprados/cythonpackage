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
import importlib.abc as abc  # Never remove this import, else the importlib.abc can not be visible with Python 3.10
import importlib.util

import sys

# Chooses the right init function
# from importlib.machinery import ModuleSpec
from typing import Optional


# @see importlib.machinery.PathFinder
class _CythonPackageMetaPathFinder(abc.MetaPathFinder):
    def __init__(self, name_filter: str, file: str):
        super(_CythonPackageMetaPathFinder, self).__init__()
        self._name_filter = name_filter
        self._file = file


    # def Xfind_spec(self, fullname, path, target=None):
    #     # TODO: manage deprecated
    #     print(f"\nfind_spec({fullname=},{path=},{target=})")
    #     try:
    #         module=fullname[0:fullname.rindex('.')]
    #     except ValueError:
    #         module = fullname
    #     print(f"{module=}")
    #     x=importlib.machinery.PathFinder.find_spec(module,path,target)
    #     #
    #     # x = importlib.machinery.PathFinder().find_spec(module)
    #     print(f"PathFinder={x=}")
    #
    #     # x= importlib.machinery.FileFinder(
    #     #     "",
    #     #     (
    #     #         importlib.machinery.ExtensionFileLoader,
    #     #         importlib.machinery.EXTENSION_SUFFIXES
    #     #     )).find_spec(module)
    #     # print(f"FileFinder={x=}")
    #     if fullname.startswith(self._name_filter):
    #         x = importlib.machinery.PathFinder().find_spec(self._name_filter)
    #     else:
    #         x = importlib.machinery.PathFinder().find_spec(module)
    #     return x
    #
    #     # return importlib.machinery.PathFinder().find_spec(fullname)
    #
    def find_module(self, fullname: str, path: str) -> Optional[importlib.machinery.ExtensionFileLoader]:
        if fullname.startswith(self._name_filter):
            # use this extension-file but PyInit-function of another module:
            return importlib.machinery.ExtensionFileLoader(fullname, self._file)


_registered_prefix = set()


def init(module_name: str) -> None:
    """ Load the compiled module, and invoke the PyInit-function of another module """
    module = importlib.import_module(module_name + '.__compile__')
    prefix = module.__name__.split('.', 1)[0] + "."
    for p in _registered_prefix:
        if prefix.startswith(p):
            break
    else:
        _registered_prefix.add(prefix)
        sys.meta_path.append(_CythonPackageMetaPathFinder(prefix, module.__file__))
