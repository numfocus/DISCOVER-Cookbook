# DISCOVER-handbook
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
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
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aterrel"><img src="https://avatars.githubusercontent.com/u/30583?v=4?s=100" width="100px;" alt="Andy R. Terrel"/><br /><sub><b>Andy R. Terrel</b></sub></a><br /><a href="#ideas-aterrel" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bozicb.github.io/about/"><img src="https://avatars.githubusercontent.com/u/5595193?v=4?s=100" width="100px;" alt="Bojan Božić"/><br /><sub><b>Bojan Božić</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=bozicb" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.oxinabox.net/"><img src="https://avatars.githubusercontent.com/u/5127634?v=4?s=100" width="100px;" alt="Frames White"/><br /><sub><b>Frames White</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=oxinabox" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://globaltech.internews.org"><img src="https://avatars.githubusercontent.com/u/7980466?v=4?s=100" width="100px;" alt="Gina"/><br /><sub><b>Gina</b></sub></a><br /><a href="#maintenance-Dr-G" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gina"><img src="https://avatars.githubusercontent.com/u/33875?v=4?s=100" width="100px;" alt="Gina"/><br /><sub><b>Gina</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Gina" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Oloni"><img src="https://avatars.githubusercontent.com/u/40644425?v=4?s=100" width="100px;" alt="Oloni"/><br /><sub><b>Oloni</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Oloni" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tkoyama010"><img src="https://avatars.githubusercontent.com/u/7513610?v=4?s=100" width="100px;" alt="Tetsuo Koyama"/><br /><sub><b>Tetsuo Koyama</b></sub></a><br /><a href="#question-tkoyama010" title="Answering Questions">💬</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!