#!/usr/bin/env python
def customize_compiler(compiler):
    """Customized to add debugging information to release builds"""
    customize_compiler.__base__(compiler)
    if compiler.compiler_type == 'unix':
        for options in (compiler.compiler, compiler.compiler_so):
            if '-g' not in options:
                options.append('-g')
    elif compiler.compiler_type == 'msvc':
        if not compiler.initialized: compiler.initialize()
        compiler.compile_options.append('/Z7')
        ldflags_debug = ('/DEBUG', '/OPT:REF', '/OPT:ICF')
        compiler.ldflags_shared.extend(ldflags_debug)
        compiler.ldflags_static.extend(ldflags_debug)
# Note that this import must be done separate as to prevent other modules
# from grabbing the customize_compiler() function before our customized
# function can be installed.
from distutils import sysconfig
customize_compiler.__base__ = sysconfig.customize_compiler
sysconfig.customize_compiler = customize_compiler

import os, re, sys
from itertools import izip
from distutils import log
from distutils.ccompiler import CCompiler
from distutils.dep_util import newer_group
from distutils.util import convert_path
_find_include = r'\s*#\s*include\s+(?:"([^"\n]+)"|<([^>\n]+)>)'
_find_include = re.compile(_find_include).match
class CCompilerEx(CCompiler):
    def _find_depends(self, source, incdirs, depends):
        source = convert_path(source)
        system_dirs = incdirs
        user_dirs = [os.path.dirname(source)] + system_dirs
        depends = set(depends)

        # do two passes to prevent having too many files open at once
        todo = []
        lines = open(source)
        for line in lines:
            match = _find_include(line)
            if match:
                user_include, system_include = map(convert_path, match.groups())
                if user_include:
                    todo.append((user_include, user_dirs))
                else:
                    todo.append((system_include, system_dirs))
        lines.close()
        # Now look for the included file on the search path
        includes = set()
        for include, search_path in todo:
            for path in search_path:
                filename = os.path.normpath(os.path.join(path, include))
                if os.path.isfile(filename) and filename not in depends:
                    depends.add(filename)
                    depends |= self._find_depends(filename, incdirs, depends)
                    break
        return depends

    def _setup_compile(self, outdir, macros, incdirs, sources, depends,
                       extra_postargs):
        macros, objects, extra_postargs, pp_opts, build = \
            CCompiler._setup_compile(self, outdir, macros, incdirs, [],
                                     depends, extra_postargs)
        if incdirs is None:
            incdirs = self.include_dirs
        else:
            incdirs = list(incdirs) + (self.include_dirs or [])
        if depends is None:
            depends = set()
        else:
            depends = set(depends)
        # Get the list of expected output files
        objects = self.object_filenames(sources,
                                        strip_dir=0,
                                        output_dir=outdir)

        # Do dependency checking
        skip_source = set()
        if self.force:
            # rebuild everything
            pass
        else:
            for src, obj in izip(sources, objects):
                deps = self._find_depends(src, incdirs, depends)
                deps.add(src)
                if not newer_group(deps, obj):
                    skip_source.add(src)
        build = {}
        for src, obj in izip(sources, objects):
            self.mkpath(os.path.dirname(obj))
            if src in skip_source:
                log.debug("skipping %s (%s up-to-date)", src, obj)
            else:
                build[obj] = src, os.path.splitext(src)[1]

        return macros, objects, extra_postargs, pp_opts, build

    def depends_pairwise(self, sources, incdirs, depends):
        if incdirs is None:
            incdirs = self.include_dirs
        else:
            incdirs = list(incdirs) + (self.include_dirs or [])
        depends = set(depends)
        pairs = []
        for source in sources:
            deps = self._find_depends(source, incdirs, depends)
            pairs.append((source, deps))
        return pairs
from distutils import ccompiler
ccompiler.CCompiler = CCompilerEx

from distutils.command.build_ext import build_ext as cmdclass
class build_ext(cmdclass):
    def build_extension(self, ext):
        try:
            pairs = self.compiler.depends_pairwise(ext.sources,
                                                   ext.include_dirs,
                                                   ext.depends)
        except:
            pass
        else:
            for source, depends in pairs:
                if newer_group(depends, source, 'newer'):
                    os.utime(source, None)
        cmdclass.build_extension(self, ext)
from distutils.command import build_ext as cmdmodule
cmdmodule.build_ext = build_ext

# -- end of custimzation ----------------------------------------------

from distutils.core import setup, Extension

# add'l setup keywords
kw = {}

setup(name='Amara',
      version='2.0a0',
      description="Library for XML processing in Python",
      long_description="Library for XML processing in Python, designed to balance the native idioms of Python with the native character of XML.",
      url='http://wiki.xml3k.org/Amara2',
      author='Amara team',
      author_email='amara-dev@googlegroups.com',
      classifiers=[
         'Development Status :: 3 - Alpha',
         'Intended Audience :: Developers',
         'License :: OSI Approved :: Apache Software License',
         'Programming Language :: Python',
         'Topic :: Software Development :: Libraries :: Python Modules',
         'Topic :: Text Processing :: Markup :: XML',
         ],
      download_url='ftp://ftp.4suite.org/pub/Amara/',
      license='Apache Software License',
      #license_file='COPYING',
      packages=['amara',
                'amara.lib',
                'amara.bindery',
                'amara.dom',
                'amara.writers',
                'amara.xpath',
                'amara.xpath.compiler',
                'amara.xpath.expressions',
                'amara.xpath.extensions',
                'amara.xpath.functions',
                'amara.xpath.locationpaths',
                'amara.xpath.parser',
                'amara.xslt',
                'amara.xslt.expressions',
                'amara.xslt.numbers',
                'amara.xslt.reader',
                'amara.xslt.tree',
                'amara.xslt.xpatterns',
                'amara.xupdate',
                # Test support; would be possible to break out into separate
                # package at some point.
                'amara.test',
                'amara.test.xslt',
                ],
      package_dir={'amara.test': 'test'},
      ext_modules=[
          Extension('amara._xmlstring',
                    sources=['amara/src/xmlstring.c'],
                    ),
          Extension('amara._expat',
                    define_macros=[('HAVE_EXPAT_CONFIG_H', None),
                                   ('Expat_BUILDING_MODULE', None),
                                   ],
                    include_dirs=['amara/src', 'amara/src/expat'],
                    sources=[# Expat XML parser
                             'amara/src/expat/lib/xmlparse.c',
                             'amara/src/expat/lib/xmlrole.c',
                             'amara/src/expat/lib/xmltok.c',
                             # Miscellaneous supporting routines
                             'amara/src/expat/util.c',
                             # XML_Char <-> PyUnicode
                             'amara/src/expat/xmlchar.c',
                             # Optimized stack implementation
                             'amara/src/expat/stack.c',
                             # XML_Char HashTable implementation
                             'amara/src/expat/hash_table.c',
                             # DTD validation support
                             'amara/src/expat/content_model.c',
                             # DTD validation support
                             'amara/src/expat/validation.c',
                             # StateTable implementation
                             'amara/src/expat/state_machine.c',
                             # basic InputSource object
                             'amara/src/expat/input_source.c',
                             # Attributes object
                             'amara/src/expat/attributes.c',
                             # ExpatReader object
                             'amara/src/expat/reader.c',
                             # Filter and Handler classes
                             'amara/src/expat/filter.c',
                             # SaxReader object
                             'amara/src/expat/sax_filter.c',
                             # Module interface
                             'amara/src/expat/expat.c',
                             ],
                    ),
          Extension('amara._domlette',
                    define_macros=[('Domlette_BUILDING_MODULE', None)],
                    include_dirs=['amara/src', 'amara/src/expat'],
                    sources=['amara/src/domlette/exceptions.c',
                             'amara/src/domlette/node.c',
                             #'amara/src/domlette/nodelist.c',
                             'amara/src/domlette/attributemap.c',
                             'amara/src/domlette/namespacemap.c',
                             'amara/src/domlette/characterdata.c',
                             'amara/src/domlette/attr.c',
                             'amara/src/domlette/element.c',
                             'amara/src/domlette/text.c',
                             'amara/src/domlette/comment.c',
                             'amara/src/domlette/processinginstruction.c',
                             'amara/src/domlette/document.c',
                             'amara/src/domlette/namespace.c',
                             # Document builder
                             'amara/src/domlette/builder.c',
                             # Reference count testing
                             'amara/src/domlette/refcounts.c',
                             # Module interface
                             'amara/src/domlette/domlette.c',
                             ],
                    ),
          Extension('amara.writers._xmlstream',
                    sources=['amara/writers/src/xmlstream.c'],
                    ),
          Extension('amara.writers.treewriter',
                    include_dirs=['amara/src', 'amara/src/domlette'],
                    sources=['amara/writers/src/treewriter.c'],
                    ),
          Extension('amara.xpath._datatypes',
                    include_dirs=['amara/src/domlette'],
                    sources=['amara/xpath/src/datatypes.c'],
                    ),
          Extension('amara.xpath.locationpaths._axes',
                    include_dirs=['amara/src/domlette'],
                    sources=['amara/xpath/src/axes.c'],
                    ),
          Extension('amara.xpath.locationpaths._nodetests',
                    include_dirs=['amara/src/domlette'],
                    sources=['amara/xpath/src/nodetests.c'],
                    ),
          Extension('amara.xpath.locationpaths._paths',
                    sources=['amara/xpath/src/paths.c'],
                    ),
          Extension('amara.xpath.parser._xpathparser',
                    sources=['amara/xpath/parser/xpathparser.c'],
                    define_macros=[('BisonGen_FORWARDS_COMPATIBLE', None)],
                    ),
          Extension('amara.xslt.expressions._avt',
                    sources=['amara/xslt/expressions/avt.c'],
                    define_macros=[('BisonGen_FORWARDS_COMPATIBLE', None)],
                    ),
          Extension('amara.xslt.xpatterns._parser',
                    sources=['amara/xslt/xpatterns/parser.c'],
                    define_macros=[('BisonGen_FORWARDS_COMPATIBLE', None)],
                    ),
          Extension('amara.xslt.tree._tree',
                    include_dirs=['amara/src'],
                    sources=['amara/xslt/src/xslt_node.c',
                             'amara/xslt/src/xslt_root.c',
                             'amara/xslt/src/xslt_text.c',
                             'amara/xslt/src/xslt_element.c',
                             'amara/xslt/src/xslt_tree.c',
                             ],
                    ),
                 ],
      **kw)

