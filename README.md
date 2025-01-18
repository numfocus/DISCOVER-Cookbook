# DISCOVER-handbook
![All Contributors](https://img.shields.io/github/all-contributors/numfocus/DISCOVER-Cookbook?color=ee8449)

The NumFOCUS DISCOVER Handbook (Diverse &amp; Inclusive Spaces and Conferences: Overall Vision and Essential Resources). A guide for organizing more diverse and inclusive events and conferences, produced by the NumFOCUS Diversity &amp; Inclusion in Scientific Computing (DISC) Program, with support from the Moore Foundation. 

If you are looking to read the book please visit https://discover-cookbook.numfocus.org/ for a live version of the book. This is the code that powers that website and is intended for maintainers and contributors.


## Ways to contribute to this repository

The original body of work took place at a series of unconferences and various spurts of energy, today the DISCOVER-cookbook is a living project with numerous contributors. Because it is code to produce a book rather than code for a software library or application, it has different needs than typical open source software systems. Because of these unique needs, we separate various types of contributions:

### Ideas, Questions, and Discussions

Please contribute ideas, questions, and discussions for content or enhancements over in [the discussions tab](https://github.com/numfocus/DISCOVER-Cookbook/discussions).

### Problems or Tracking of Work Items from Ideas, Questions, or Discussions

Please add issues on [the github issue tracker](https://github.com/numfocus/DISCOVER-Cookbook/discussions). 

### Content and Design

While content is the heart of the project, the quality of the content needs to remain high. Due to a high volume of generated text being submitted for review, content takes longer to review and approve. We value these contributions but just understand that it will take time to add. Please start an idea in the discussions, then move to making an issue once there is approval for the content to be added to the book. After that issue is made we feel free to open [a pull request](https://github.com/numfocus/DISCOVER-Cookbook/pulls) against the repository to begin the review process.

### Bug fixes

For issues with other elements of the book, first make sure an issue is open and tracking can occur on the issue. Then open a a pull request](https://github.com/numfocus/DISCOVER-Cookbook/pulls).

### See Also

For more information, see the `contributing.md` file with a fuller guide on how to contribute.


## How to run the book locally

Create a local python environment and install all the required dependencies using the following commands (either with conda or pip)

### If Using Conda
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

### If Using pip
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
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Akhil-Jasson"><img src="https://avatars.githubusercontent.com/u/114808672?v=4?s=100" width="100px;" alt="Akhil-Jasson"/><br /><sub><b>Akhil-Jasson</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Akhil-Jasson" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aterrel"><img src="https://avatars.githubusercontent.com/u/30583?v=4?s=100" width="100px;" alt="Andy R. Terrel"/><br /><sub><b>Andy R. Terrel</b></sub></a><br /><a href="#ideas-aterrel" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3Aaterrel" title="Reviewed Pull Requests">👀</a> <a href="#maintenance-aterrel" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ashleymaguire"><img src="https://avatars.githubusercontent.com/u/3665420?v=4?s=100" width="100px;" alt="Ashley Maguire"/><br /><sub><b>Ashley Maguire</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=ashleymaguire" title="Documentation">📖</a> <a href="#maintenance-ashleymaguire" title="Maintenance">🚧</a> <a href="#ideas-ashleymaguire" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><img src="https://avatars.githubusercontent.com/u/114808672?v=4?s=100" width="100px;" alt="Ashley Otero"/><br /><sub><b>Ashley Otero</b></sub><br /><a href="#ideas" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bozicb.github.io/about/"><img src="https://avatars.githubusercontent.com/u/5595193?v=4?s=100" width="100px;" alt="Bojan Božić"/><br /><sub><b>Bojan Božić</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=bozicb" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://chrisholdgraf.com"><img src="https://avatars.githubusercontent.com/u/1839645?v=4?s=100" width="100px;" alt="Chris Holdgraf"/><br /><sub><b>Chris Holdgraf</b></sub></a><br /><a href="#ideas-choldgraf" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://galaxyproject.org/people/dave-clements/"><img src="https://avatars.githubusercontent.com/u/1622414?v=4?s=100" width="100px;" alt="Dave Clements"/><br /><sub><b>Dave Clements</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=tnabtaf" title="Documentation">📖</a> <a href="#maintenance-tnabtaf" title="Maintenance">🚧</a> <a href="#ideas-tnabtaf" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://www.oxinabox.net/"><img src="https://avatars.githubusercontent.com/u/5127634?v=4?s=100" width="100px;" alt="Frames White"/><br /><sub><b>Frames White</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=oxinabox" title="Documentation">📖</a> <a href="#ideas-oxinabox" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://globaltech.internews.org"><img src="https://avatars.githubusercontent.com/u/7980466?v=4?s=100" width="100px;" alt="Gina"/><br /><sub><b>Gina</b></sub></a><br /><a href="#maintenance-Dr-G" title="Maintenance">🚧</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Dr-G" title="Documentation">📖</a> <a href="#ideas-Dr-G" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3ADr-G" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gina"><img src="https://avatars.githubusercontent.com/u/33875?v=4?s=100" width="100px;" alt="Gina"/><br /><sub><b>Gina</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Gina" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Jeffrin2005"><img src="https://avatars.githubusercontent.com/u/135723871?v=4?s=100" width="100px;" alt="Jeffrin Jojo"/><br /><sub><b>Jeffrin Jojo</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Jeffrin2005" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/dedx"><img src="https://avatars.githubusercontent.com/u/1399548?v=4?s=100" width="100px;" alt="Jennifer Klay"/><br /><sub><b>Jennifer Klay</b></sub></a><br /><a href="#ideas-dedx" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kafui4k"><img src="https://avatars.githubusercontent.com/u/14028900?v=4?s=100" width="100px;" alt="Kafui Alordo"/><br /><sub><b>Kafui Alordo</b></sub></a><br /><a href="#ideas-kafui4k" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kasiarachuta-zz"><img src="https://avatars.githubusercontent.com/u/15620575?v=4?s=100" width="100px;" alt="Kasia Rachuta"/><br /><sub><b>Kasia Rachuta</b></sub></a><br /><a href="#ideas-kasiarachuta-zz" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/katsel"><img src="https://avatars.githubusercontent.com/u/6429934?v=4?s=100" width="100px;" alt="Kat Hoessel"/><br /><sub><b>Kat Hoessel</b></sub></a><br /><a href="#ideas-katsel" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Kmwai"><img src="https://avatars.githubusercontent.com/u/6900704?v=4?s=100" width="100px;" alt="M.K"/><br /><sub><b>M.K</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Kmwai" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://munkm.github.io"><img src="https://avatars.githubusercontent.com/u/6745434?v=4?s=100" width="100px;" alt="Madicken Munk"/><br /><sub><b>Madicken Munk</b></sub></a><br /><a href="#ideas-munkm" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://mikofski.github.io/"><img src="https://avatars.githubusercontent.com/u/1385621?v=4?s=100" width="100px;" alt="Mark Mikofski"/><br /><sub><b>Mark Mikofski</b></sub></a><br /><a href="#maintenance-mikofski" title="Maintenance">🚧</a> <a href="#ideas-mikofski" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=mikofski" title="Documentation">📖</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3Amikofski" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://salman-ch.netlify.app"><img src="https://avatars.githubusercontent.com/u/151463017?v=4?s=100" width="100px;" alt="Muhammad Salman"/><br /><sub><b>Muhammad Salman</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=SalmanDeveloperz" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://linkedin.com/in/noatamir"><img src="https://avatars.githubusercontent.com/u/6564007?v=4?s=100" width="100px;" alt="Noa Tamir"/><br /><sub><b>Noa Tamir</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3Anoatamir" title="Reviewed Pull Requests">👀</a> <a href="#ideas-noatamir" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-noatamir" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Oloni"><img src="https://avatars.githubusercontent.com/u/40644425?v=4?s=100" width="100px;" alt="Oloni"/><br /><sub><b>Oloni</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Oloni" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/pratham15541"><img src="https://avatars.githubusercontent.com/u/109359719?v=4?s=100" width="100px;" alt="Pratham "/><br /><sub><b>Pratham </b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=pratham15541" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://rgaiacs.com"><img src="https://avatars.githubusercontent.com/u/1506457?v=4?s=100" width="100px;" alt="Raniere Silva"/><br /><sub><b>Raniere Silva</b></sub></a><br /><a href="#ideas-rgaiacs" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://reshamas.github.io"><img src="https://avatars.githubusercontent.com/u/2507232?v=4?s=100" width="100px;" alt="Reshama Shaikh"/><br /><sub><b>Reshama Shaikh</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=reshamas" title="Documentation">📖</a> <a href="#ideas-reshamas" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.sarahsupp.org"><img src="https://avatars.githubusercontent.com/u/1189512?v=4?s=100" width="100px;" alt="Sarah Supp"/><br /><sub><b>Sarah Supp</b></sub></a><br /><a href="#ideas-sarahsupp" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://trallard.dev"><img src="https://avatars.githubusercontent.com/u/23552331?v=4?s=100" width="100px;" alt="Tania Allard"/><br /><sub><b>Tania Allard</b></sub></a><br /><a href="#maintenance-trallard" title="Maintenance">🚧</a> <a href="#ideas-trallard" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://terezaiofciu.com"><img src="https://avatars.githubusercontent.com/u/6162692?v=4?s=100" width="100px;" alt="Tereza Iofciu"/><br /><sub><b>Tereza Iofciu</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=terezaif" title="Documentation">📖</a> <a href="#maintenance-terezaif" title="Maintenance">🚧</a> <a href="#ideas-terezaif" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tkoyama010"><img src="https://avatars.githubusercontent.com/u/7513610?v=4?s=100" width="100px;" alt="Tetsuo Koyama"/><br /><sub><b>Tetsuo Koyama</b></sub></a><br /><a href="#question-tkoyama010" title="Answering Questions">💬</a> <a href="#maintenance-tkoyama010" title="Maintenance">🚧</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=tkoyama010" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/discover-cookbook"><img src="https://avatars.githubusercontent.com/u/43108644?v=4?s=100" width="100px;" alt="discover-cookbook"/><br /><sub><b>discover-cookbook</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=discover-cookbook" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kasiarachuta"><img src="https://avatars.githubusercontent.com/u/64444247?v=4?s=100" width="100px;" alt="kasiarachuta"/><br /><sub><b>kasiarachuta</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=kasiarachuta" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
