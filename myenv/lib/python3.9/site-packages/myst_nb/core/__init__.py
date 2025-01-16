"""Modules for core functionality.

The parsing of a notebook consists of a number of stages,
with each stage separated into a separate module:

1. The configuration is set (from a file or CLI)
2. The parser is called with an input string and source
3. The parser reads the input string to a notebook node
4. The notebook is converted to a Markdown-It tokens syntax tree
5. The notebook code outputs are potentially updated, via execution or from a cache
6. The syntax tree is transformed to a docutils document AST (calling the renderer plugin)
7. The docutils document is processed by docutils/sphinx, to create the desired output format(s)
"""
