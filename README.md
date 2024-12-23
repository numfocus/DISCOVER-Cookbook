# DISCOVER-handbook
The NumFOCUS DISCOVER Handbook (Diverse &amp; Inclusive Spaces and Conferences: Overall Vision and Essential Resources). A guide for organizing more diverse and inclusive events and conferences, produced by the NumFOCUS Diversity &amp; Inclusion in Scientific Computing (DISC) Program, with support from the Moore Foundation. 


# How to run the book locally

Create a local python environment and install the **jupyter-book** and **sphinx-tags** (either conda or pip)

Using pip
``` sh
pip install jupyter-book sphinx-tags
```

Using Conda
```sh
conda install -c conda-forge jupyter-book sphinx-tags
```

Once the setup is complete, build using:
``` sh
jupyter-book build DISCOVER
```