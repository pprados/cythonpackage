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
import io
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union

from Cython.Build import cythonize
from setuptools import Extension
from setuptools.command.build_py import build_py as original_build_py


_conf = {
    "inject_ext_modules": True,
    "inject_init": True,
    "remove_source": True,
    "compile_pyc": True,
    "optimize": 2,
}


def _compile_packages(packages: List[str]) -> List[Extension]:
    extensions: List[Extension] = []
    if not packages:
        return extensions
    for package in packages:
        root = Path(package, "__compile__.py")
        if root.exists():
            package_path = str(root.parent)
            sourcefiles = [str(path) for path in Path(package_path).rglob('*.pyx')]
            sourcefiles += [str(path) for path in Path(package_path).rglob('*.py')
                            if path.name not in ["__init__.py", "__compile__.py"]]
            sourcefiles.append(package_path + "/__compile__.py")
            # print(f'Extension(name="{package_path}.__compile__", sources={sourcefiles})')
            if sourcefiles:
                extensions.append(Extension(
                    name=f"{package_path}.__compile__",
                    sources=sourcefiles,
                ))
    return extensions


class _build_py(original_build_py):
    """ build_py to remove the source file for compiled package """

    def finalize_options(self):
        super().finalize_options()
        self.compile = _conf["compile_pyc"]
        self.optimize = _conf["optimize"]
        self.remove_source = _conf["remove_source"]
        self.inject_init = _conf["inject_init"]
        self._patched_init = []

    def find_package_modules(self, package: str, package_dir: str) -> List[Tuple[str, str, str]]:
        modules: List[Tuple[str, str, str]] = super().find_package_modules(package, package_dir)
        if self.remove_source:
            filtered_modules = []
            for (pkg, mod, filepath) in modules:
                _path = Path(filepath)
                if (_path.suffix in [".py", ".pyx"] and
                        "__init__.py" != _path.name and
                        Path(_path.parent, "__compile__.py").exists()):
                    continue
                filtered_modules.append((pkg, mod, filepath,))
            return filtered_modules
        else:
            return modules

    def find_data_files(self, package, src_dir):
        """Return filenames for package's data files in 'src_dir'"""
        # Remove the source code via the data_files
        data_files = super().find_data_files(package, src_dir)
        if self.remove_source:
            filtered_datas: List[str] = []
            for f in data_files:
                _path = Path(f)
                if (_path.suffix in [".c", ".py", ".pyx"] and
                        # "__init__.py" != _path.name and
                        Path(_path.parent, "__compile__.py").exists()):
                    continue
                filtered_datas.append(f)
            return filtered_datas
        else:
            return data_files

    def build_module(self, module, module_file, package):
        outfile, copied = super().build_module(module, module_file, package)
        inject = "import cythonpackage; cythonpackage.init(__name__);"
        if self.inject_init:
            if outfile.endswith("__init__.py"):
                package_file = package.replace('.', '/')
                if outfile.endswith("__init__.py") and Path(package_file, "__compile__.py").exists():
                    # Patch the __init__.py inject the initialisation
                    with io.open(outfile, encoding="utf-8-sig") as f:
                        lines = f.readlines()
                    update = False
                    for i, line in enumerate(lines):
                        if line.strip().startswith("#"):
                            continue
                        if not line.startswith(inject):
                            lines[i] = inject + line
                            update = True
                        break
                    else:
                        lines.append(inject)
                        update = True
                    if update:
                        with io.open(outfile, "w", encoding="utf-8-sig") as f:
                            f.writelines(lines)
        return outfile, copied


def build_cythonpackage(setup: Dict[str, Any], conf: Union[bool, Dict[str, Any]] = True):
    """ Plugin for setuptools """
    global _conf
    if not conf:
        return
    if isinstance(conf, dict):
        _conf = {**_conf, **conf}

    if _conf["inject_ext_modules"]:
        packages = setup.get('packages', [])
        ext_modules = setup.get('ext_modules', [])
        compiled_module = cythonize(_compile_packages(packages),
                                    compiler_directives={'language_level': 3},
                                    build_dir="build/cythonpackage"
                                    )
        if ext_modules:
            ext_modules.extend(compiled_module)
        else:
            setup['ext_modules'] = compiled_module

    # Extend the build process to remove the compiled source code
    cmdclass = setup.get('cmdclass', {})
    cmdclass['build_py'] = _build_py
    setup['cmdclass'] = cmdclass

    install_requires = setup.get('install_requires', [])
    if install_requires is None:
        install_requires = []
    if 'cythonpackage' not in install_requires:
        install_requires.append('cythonpackage')
        setup['install_requires'] = install_requires

    if 'CFLAGS' not in os.environ:
        os.environ['CFLAGS'] = '-O3'


# Plugin for setup.py
def cythonpackage(setup, attr, value: Union[bool, Dict[str, Any]]):
    build_cythonpackage(vars(setup), value)



