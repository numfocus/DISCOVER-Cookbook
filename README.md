# DISCOVER-Cookbook
![All Contributors](https://img.shields.io/github/all-contributors/numfocus/DISCOVER-Cookbook?color=ee8449)

The NumFOCUS DISCOVER Cookbook (Diverse &amp; Inclusive Spaces and Conferences: Overall Vision and Essential Resources). A guide for organizing more diverse and inclusive events and conferences, produced by the NumFOCUS Diversity &amp; Inclusion in Scientific Computing (DISC) Program, with support from the Moore Foundation. 

If you are looking to read the book please visit https://discover-cookbook.numfocus.org/ for a live version of the book. This is the code that powers that website and is intended for maintainers and contributors.


## Ways to contribute to this repository

The original body of work took place at a series of unconferences and various spurts of energy, today the DISCOVER-cookbook is a living project with numerous contributors. Because it is code to produce a book rather than code for a software library or application, it has different needs than typical open source software systems. Because of these unique needs, we separate various types of contributions:

### Ideas, Questions, and Discussions

Please contribute ideas, questions, and discussions for content or enhancements over in [the discussions tab](https://github.com/numfocus/DISCOVER-Cookbook/discussions).

### Problems or Tracking of Work Items from Ideas, Questions, or Discussions

Please add issues on [the GitHub issue tracker](https://github.com/numfocus/DISCOVER-Cookbook/issues). 

### Content and Design

While content is the heart of the project, the quality of the content needs to remain high. Due to a high volume of generated text being submitted for review, content takes longer to review and approve. We value these contributions but just understand that it will take time to add. Please start an idea in the discussions, then move to making an issue once there is approval for the content to be added to the book. After that issue is made we feel free to open [a pull request](https://github.com/numfocus/DISCOVER-Cookbook/pulls) against the repository to begin the review process.

### Bug fixes

For issues with other elements of the book, first make sure an issue is open and tracking can occur on the issue. Then open a a [pull request](https://github.com/numfocus/DISCOVER-Cookbook/pulls).

> **Note:** To contribute effectively, check for active pull requests to avoid duplication, discuss your ideas in active issues or pull requests, and seek approval from maintainers or issue creators before proceeding. Respect others' contributions and collaborate constructively to improve the project.

### Contribution Workflow

To contribute changes:

1. **Fork the Repository**: Click the "Fork" button at the top-right of this repository's GitHub page to create a copy in your account.

2. **Clone Your Fork**:
   ```sh
   git clone https://github.com/your-username/DISCOVER-Cookbook.git
   cd DISCOVER-Cookbook
   ```

3. **Create a New Branch**:
   ```sh
   git checkout -b your-branch-name
   ```

4. **Make Changes**: 
   - Edit files in your preferred editor
   - Build and verify your changes locally using the [build instructions](#how-to-run-the-book-locally) below
   
5. **Test Locally**: Build the book and view your changes:
   ```sh
   jupyter-book build DISCOVER
   python -m http.server 8000 --directory DISCOVER/_build/html/
   ```
   Visit [`http://localhost:8000`](http://localhost:8000) in your browser to verify changes.

6. **Commit and Push**:
   ```sh
   git add .
   git commit -m "Description of your changes"
   git push origin your-branch-name
   ```

7. **Open a Pull Request**: Navigate to your fork on GitHub, select your branch, and click "New Pull Request". Provide a clear description of your changes.


### For More Information

See the [contributing.md](CONTRIBUTING.md) for a detailed guide on how to contribute.


## How to run the book locally

Create a local python environment and install all the required dependencies using the following commands (either with conda or pip)

### If Using Conda
1. Create the Conda Environment
```sh
conda env create -f environment.yml
```
2. Activate the Conda Environment
```sh
conda activate DISCOVER-Cookbook
```
3. Finally, to build the Jupyter Book
``` sh
jupyter-book build DISCOVER
```

### If Using pip
1. Create a Virtual Environment (optional)
```sh
python -m venv .venv
```
2. Activate the virtual Environment (optional)
- on Windows:
```sh
.venv\Scripts\activate
```
- on macOS/Linux:
```sh
source .venv/bin/activate
```
3. Install the required dependencies
```sh
pip install -r requirements.txt
```
4. Finally, to build the Jupyter Book
``` sh
jupyter-book build DISCOVER
```
### View Locally  
After building, you can view the book in one of the following ways:  

#### **Option 1: Using a Local Server**  
Run the following command to start a local server:  
```sh
python -m http.server 8000 --directory DISCOVER/_build/html/
```
Then, open [`http://localhost:8000`](http://localhost:8000) in your browser.  

#### **Option 2: Opening the File Directly**  
Alternatively, you can open the book directly by navigating to:  
```
DISCOVER/_build/html/index.html
```
and opening it in your browser.  

> **Note:** Make sure you have built the book again before accessing it.




## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Akhil-Jasson"><img src="https://avatars.githubusercontent.com/u/114808672?v=4?s=100" width="100px;" alt="Akhil-Jasson"/><br /><sub><b>Akhil-Jasson</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Akhil-Jasson" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aterrel"><img src="https://avatars.githubusercontent.com/u/30583?v=4?s=100" width="100px;" alt="Andy R. Terrel"/><br /><sub><b>Andy R. Terrel</b></sub></a><br /><a href="#ideas-aterrel" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3Aaterrel" title="Reviewed Pull Requests">👀</a> <a href="#maintenance-aterrel" title="Maintenance">🚧</a> <a href="#question-aterrel" title="Answering Questions">💬</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Iamanujosh"><img src="https://avatars.githubusercontent.com/u/88044065?v=4?s=100" width="100px;" alt="Anushka joshi"/><br /><sub><b>Anushka joshi</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Iamanujosh" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/AR21SM"><img src="https://avatars.githubusercontent.com/u/179873264?v=4?s=100" width="100px;" alt="Ashish Mahajan"/><br /><sub><b>Ashish Mahajan</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=AR21SM" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ashleymaguire"><img src="https://avatars.githubusercontent.com/u/3665420?v=4?s=100" width="100px;" alt="Ashley Maguire"/><br /><sub><b>Ashley Maguire</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=ashleymaguire" title="Documentation">📖</a> <a href="#maintenance-ashleymaguire" title="Maintenance">🚧</a> <a href="#ideas-ashleymaguire" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><img src="https://avatars.githubusercontent.com/u/114808672?v=4?s=100" width="100px;" alt="Ashley Otero"/><br /><sub><b>Ashley Otero</b></sub><br /><a href="#ideas" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://bozicb.github.io/about/"><img src="https://avatars.githubusercontent.com/u/5595193?v=4?s=100" width="100px;" alt="Bojan Božić"/><br /><sub><b>Bojan Božić</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=bozicb" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://chrisholdgraf.com"><img src="https://avatars.githubusercontent.com/u/1839645?v=4?s=100" width="100px;" alt="Chris Holdgraf"/><br /><sub><b>Chris Holdgraf</b></sub></a><br /><a href="#ideas-choldgraf" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://danielskatz.org"><img src="https://avatars.githubusercontent.com/u/2913845?v=4?s=100" width="100px;" alt="Daniel S. Katz"/><br /><sub><b>Daniel S. Katz</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=danielskatz" title="Code">💻</a> <a href="#maintenance-danielskatz" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://galaxyproject.org/people/dave-clements/"><img src="https://avatars.githubusercontent.com/u/1622414?v=4?s=100" width="100px;" alt="Dave Clements"/><br /><sub><b>Dave Clements</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=tnabtaf" title="Documentation">📖</a> <a href="#maintenance-tnabtaf" title="Maintenance">🚧</a> <a href="#ideas-tnabtaf" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.oxinabox.net/"><img src="https://avatars.githubusercontent.com/u/5127634?v=4?s=100" width="100px;" alt="Frames White"/><br /><sub><b>Frames White</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=oxinabox" title="Documentation">📖</a> <a href="#ideas-oxinabox" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://globaltech.internews.org"><img src="https://avatars.githubusercontent.com/u/7980466?v=4?s=100" width="100px;" alt="Gina"/><br /><sub><b>Gina</b></sub></a><br /><a href="#maintenance-Dr-G" title="Maintenance">🚧</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Dr-G" title="Documentation">📖</a> <a href="#ideas-Dr-G" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3ADr-G" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/gina"><img src="https://avatars.githubusercontent.com/u/33875?v=4?s=100" width="100px;" alt="Gina"/><br /><sub><b>Gina</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Gina" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Jeffrin2005"><img src="https://avatars.githubusercontent.com/u/135723871?v=4?s=100" width="100px;" alt="Jeffrin Jojo"/><br /><sub><b>Jeffrin Jojo</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Jeffrin2005" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/dedx"><img src="https://avatars.githubusercontent.com/u/1399548?v=4?s=100" width="100px;" alt="Jennifer Klay"/><br /><sub><b>Jennifer Klay</b></sub></a><br /><a href="#ideas-dedx" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kafui4k"><img src="https://avatars.githubusercontent.com/u/14028900?v=4?s=100" width="100px;" alt="Kafui Alordo"/><br /><sub><b>Kafui Alordo</b></sub></a><br /><a href="#ideas-kafui4k" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kamila-NF"><img src="https://avatars.githubusercontent.com/u/142047555?v=4?s=100" width="100px;" alt="Kamila Stepniowska"/><br /><sub><b>Kamila Stepniowska</b></sub></a><br /><a href="#maintenance-kamila-NF" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/karanveerksb"><img src="https://avatars.githubusercontent.com/u/143838558?v=4?s=100" width="100px;" alt="Karanveer Singh"/><br /><sub><b>Karanveer Singh</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=karanveerksb" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kasiarachuta-zz"><img src="https://avatars.githubusercontent.com/u/15620575?v=4?s=100" width="100px;" alt="Kasia Rachuta"/><br /><sub><b>Kasia Rachuta</b></sub></a><br /><a href="#ideas-kasiarachuta-zz" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/katsel"><img src="https://avatars.githubusercontent.com/u/6429934?v=4?s=100" width="100px;" alt="Kat Hoessel"/><br /><sub><b>Kat Hoessel</b></sub></a><br /><a href="#ideas-katsel" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Kmwai"><img src="https://avatars.githubusercontent.com/u/6900704?v=4?s=100" width="100px;" alt="M.K"/><br /><sub><b>M.K</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Kmwai" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://munkm.github.io"><img src="https://avatars.githubusercontent.com/u/6745434?v=4?s=100" width="100px;" alt="Madicken Munk"/><br /><sub><b>Madicken Munk</b></sub></a><br /><a href="#ideas-munkm" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://mikofski.github.io/"><img src="https://avatars.githubusercontent.com/u/1385621?v=4?s=100" width="100px;" alt="Mark Mikofski"/><br /><sub><b>Mark Mikofski</b></sub></a><br /><a href="#maintenance-mikofski" title="Maintenance">🚧</a> <a href="#ideas-mikofski" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=mikofski" title="Documentation">📖</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3Amikofski" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://melissawm.github.io"><img src="https://avatars.githubusercontent.com/u/3949932?v=4?s=100" width="100px;" alt="Melissa Weber Mendonça"/><br /><sub><b>Melissa Weber Mendonça</b></sub></a><br /><a href="#ideas-melissawm" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://salman-ch.netlify.app"><img src="https://avatars.githubusercontent.com/u/151463017?v=4?s=100" width="100px;" alt="Muhammad Salman"/><br /><sub><b>Muhammad Salman</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=SalmanDeveloperz" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://linkedin.com/in/noatamir"><img src="https://avatars.githubusercontent.com/u/6564007?v=4?s=100" width="100px;" alt="Noa Tamir"/><br /><sub><b>Noa Tamir</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3Anoatamir" title="Reviewed Pull Requests">👀</a> <a href="#ideas-noatamir" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-noatamir" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Oloni"><img src="https://avatars.githubusercontent.com/u/40644425?v=4?s=100" width="100px;" alt="Oloni"/><br /><sub><b>Oloni</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=Oloni" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/pratham15541"><img src="https://avatars.githubusercontent.com/u/109359719?v=4?s=100" width="100px;" alt="Pratham "/><br /><sub><b>Pratham </b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=pratham15541" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/parharti"><img src="https://avatars.githubusercontent.com/u/140067623?v=4?s=100" width="100px;" alt="Prisha Sharma "/><br /><sub><b>Prisha Sharma </b></sub></a><br /><a href="#content-parharti" title="Content">🖋</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/trivia67"><img src="https://avatars.githubusercontent.com/u/137710127?v=4?s=100" width="100px;" alt="Priya Kholiya"/><br /><sub><b>Priya Kholiya</b></sub></a><br /><a href="#ideas-trivia67" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://rgaiacs.com"><img src="https://avatars.githubusercontent.com/u/1506457?v=4?s=100" width="100px;" alt="Raniere Silva"/><br /><sub><b>Raniere Silva</b></sub></a><br /><a href="#ideas-rgaiacs" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://reshamas.github.io"><img src="https://avatars.githubusercontent.com/u/2507232?v=4?s=100" width="100px;" alt="Reshama Shaikh"/><br /><sub><b>Reshama Shaikh</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=reshamas" title="Documentation">📖</a> <a href="#ideas-reshamas" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/riteshdavv"><img src="https://avatars.githubusercontent.com/u/137779094?v=4?s=100" width="100px;" alt="Ritesh Kumar Singh"/><br /><sub><b>Ritesh Kumar Singh</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=riteshdavv" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://rivaquiroga.cl/"><img src="https://avatars.githubusercontent.com/u/31421616?v=4?s=100" width="100px;" alt="Riva Quiroga"/><br /><sub><b>Riva Quiroga</b></sub></a><br /><a href="#ideas-rivaquiroga" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=rivaquiroga" title="Code">💻</a> <a href="#maintenance-rivaquiroga" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.sarahsupp.org"><img src="https://avatars.githubusercontent.com/u/1189512?v=4?s=100" width="100px;" alt="Sarah Supp"/><br /><sub><b>Sarah Supp</b></sub></a><br /><a href="#ideas-sarahsupp" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://trallard.dev"><img src="https://avatars.githubusercontent.com/u/23552331?v=4?s=100" width="100px;" alt="Tania Allard"/><br /><sub><b>Tania Allard</b></sub></a><br /><a href="#maintenance-trallard" title="Maintenance">🚧</a> <a href="#ideas-trallard" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://terezaiofciu.com"><img src="https://avatars.githubusercontent.com/u/6162692?v=4?s=100" width="100px;" alt="Tereza Iofciu"/><br /><sub><b>Tereza Iofciu</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=terezaif" title="Documentation">📖</a> <a href="#maintenance-terezaif" title="Maintenance">🚧</a> <a href="#ideas-terezaif" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tkoyama010"><img src="https://avatars.githubusercontent.com/u/7513610?v=4?s=100" width="100px;" alt="Tetsuo Koyama"/><br /><sub><b>Tetsuo Koyama</b></sub></a><br /><a href="#question-tkoyama010" title="Answering Questions">💬</a> <a href="#maintenance-tkoyama010" title="Maintenance">🚧</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=tkoyama010" title="Documentation">📖</a> <a href="https://github.com/numfocus/DISCOVER-Cookbook/pulls?q=is%3Apr+reviewed-by%3Atkoyama010" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/discover-cookbook"><img src="https://avatars.githubusercontent.com/u/43108644?v=4?s=100" width="100px;" alt="discover-cookbook"/><br /><sub><b>discover-cookbook</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=discover-cookbook" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kasiarachuta"><img src="https://avatars.githubusercontent.com/u/64444247?v=4?s=100" width="100px;" alt="kasiarachuta"/><br /><sub><b>kasiarachuta</b></sub></a><br /><a href="https://github.com/numfocus/DISCOVER-Cookbook/commits?author=kasiarachuta" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
