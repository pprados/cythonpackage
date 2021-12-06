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
from .init import init
__all__ = ['init']

try:
    import setuptools
    from .build import build_cythonpackage, cythonpackage

    __all__ = ['init', 'build_cythonpackage', "cythonpackage"]
except ImportError:
    pass  # Ignore. Use in runtime, not in build time
