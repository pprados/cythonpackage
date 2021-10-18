# Version avec PBR
# from setuptools import setup
# setup(
#     setup_requires=['pbr', 'cythonpackage'],
#     cythonpackage=False,
#     pbr=True,
#     requires=['cythonpackage'],
# )

# Version sans PBR
from setuptools import setup, find_packages

setup(
    # ext_modules=cythonize(
    #     [
    #         Extension(name="foo.__compile__",
    #                   sources=[
    #                       'foo/__compile__.py', 'foo/bar_a.py', 'foo/bar_b.py',
    #                       # 'foo/sub/__compile__.py',
    #                       'foo/sub/sub.py'
    #                   ]),
    #         Extension(name="foo.sub.__compile__",
    #                   sources=[])
    #     ],
    #     # Original produit
    #     # [
    #     #     Extension(name="foo.__compile__",
    #     #               sources=['foo/__compile__.py', 'foo/bar_a.py', 'foo/bar_b.py', 'foo/sub/__compile__.py', 'foo/sub/sub.py']),
    #     #     Extension(name="foo.sub.__compile__",
    #     #               sources=[])
    #     # ],
    #     build_dir="build/cythonpackage",
    #     compiler_directives={'language_level': 3}
    # ),
    # cmdclass={"build_py":cythonpackage._build_py},
    setup_requires=['cythonpackage'],
    cythonpackage={
        "inject_ext_modules": True,
        "remove_source": True,
        "compile_pyc": True,
        "inject_init": True,
    },

    packages=find_packages(),
    install_requires=['cythonpackage'],
)
