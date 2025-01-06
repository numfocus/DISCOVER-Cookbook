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

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):


<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!


