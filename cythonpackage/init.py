import importlib
import sys

# Chooses the right init function
from typing import Optional


class _CythonPackageMetaPathFinder(importlib.abc.MetaPathFinder):
    def __init__(self, name_filter: str, file: str):
        super(_CythonPackageMetaPathFinder, self).__init__()
        self._name_filter = name_filter
        self._file = file

    def find_module(self, fullname: str, path: str) -> Optional[importlib.machinery.ExtensionFileLoader]:
        if fullname.startswith(self._name_filter):
            # use this extension-file but PyInit-function of another module:
            return importlib.machinery.ExtensionFileLoader(fullname, self._file)


_registered_prefix=set()
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
