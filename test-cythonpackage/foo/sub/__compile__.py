# See https://newbedev.com/collapse-multiple-submodules-to-one-cython-extension
import sys
import importlib

# Chooses the right init function
# class CythonPackageMetaPathFinder(importlib.abc.MetaPathFinder):
#     def __init__(self, name_filter):
#         super(CythonPackageMetaPathFinder, self).__init__()
#         self.name_filter =  name_filter
#
#     def find_module(self, fullname, path):
#         if fullname.startswith(self.name_filter):
#             # use this extension-file but PyInit-function of another module:
#             return importlib.machinery.ExtensionFileLoader(fullname,__file__)
#
#
# # injecting custom finder/loaders into sys.meta_path:
# def bootstrap_cython_submodules():
#     print("__compile__ bootstrap")
#     sys.meta_path.append(CythonPackageMetaPathFinder(__name__.split('.',1)[0]+"."))

# from cythonpackage import _CythonPackageMetaPathFinder
# def bootstrap_cython_submodules():
#      print(f'name={__name__.split(".", 1)[0] + "."} file={__file__}')
#      sys.meta_path.append(_CythonPackageMetaPathFinder(__name__.split('.', 1)[0] + ".", __file__))