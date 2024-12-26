# DISCOVER-handbook
The NumFOCUS DISCOVER Handbook (Diverse &amp; Inclusive Spaces and Conferences: Overall Vision and Essential Resources). A guide for organizing more diverse and inclusive events and conferences, produced by the NumFOCUS Diversity &amp; Inclusion in Scientific Computing (DISC) Program, with support from the Moore Foundation. 


# How to run the book locally

Create a local python environment and install all the required dependencies using the following commands (either with conda or pip)

## If Using Conda
1. Create the Conda Environment
```sh
conda env create -f environment.yml
```
2. Activate the Conda Environment
```sh
conda activate DISCOVER-handbook
```
3. Finally, to build the Jupyter Book
``` sh
jupyter-book build DISCOVER
```

## If Using pip
1. Create a Virtual Environment (optional)
```sh
python -m venv myenv
```
2. Activate the virtual Environment (optional)
- on Windows:
```sh
myenv\Scripts\activate
```
- on macOS/Linux:
```sh
source myenv/bin/activate
```
3. Install the required dependencies
```sh
pip install -r requirements.txt
```
4. Finally, to build the Jupyter Book
``` sh
jupyter-book build DISCOVER
```