"""A docutils/sphinx parser for Jupyter Notebooks."""
__version__ = "1.1.2"


def setup(app):
    """Sphinx extension setup."""
    # we import this locally, so sphinx is not automatically imported
    from .sphinx_ext import sphinx_setup

    return sphinx_setup(app)


def glue(name: str, variable, display: bool = True) -> None:
    """Glue a variable into the notebook's cell metadata.

    Parameters
    ----------
    name: string
        A unique name for the variable. You can use this name to refer to the variable
        later on.
    variable: Python object
        A variable in Python for which you'd like to store its display value. This is
        not quite the same as storing the object itself - the stored information is
        what is *displayed* when you print or show the object in a Jupyter Notebook.
    display: bool
        Display the object you are gluing. This is helpful in sanity-checking the
        state of the object at glue-time.
    """
    # we import this locally, so IPython is not automatically imported
    from myst_nb.ext.glue import glue

    return glue(name, variable, display)
