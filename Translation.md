# Managing Translations

To support localization efforts, follow these steps to extract translatable strings and update translations.

## Generating `.pot` Files  

To extract translatable text and generate `.pot` files, run:

```sh
sphinx-build -b gettext DISCOVER/ DISCOVER/_build/gettext
```
This will store extracted strings in .pot files inside DISCOVER/_build/gettext.

## Updating .po Files
To update existing translations, use the following command:

```sh
sphinx-intl update -p DISCOVER/_build/gettext -l <language-code>
```
Replace <language-code> with your target language (e.g., en, fr, de).


## Using Transifex for Translation Management

We use [Transifex](https://app.transifex.com/numfocus/DISCOVER-Cookbook/) to manage and coordinate translation efforts for the DISCOVER Cookbook.

---

### Auto-Generating `.tx/config`

To track multiple `.po` files in Transifex, run:

```sh
python generate_tx_config.py
```
This creates or updates .tx/config so each .po file is mapped as a Transifex resource.

### Pushing to Transifex

Push source files (English):

```sh
tx push -s
```
Push specific language translations (e.g. Spanish):

```sh
tx push -t -l es
```
Run these whenever source content changes or new translations are added locally.

### Pulling Translations from Transifex

To fetch the latest translations from Transifex:
```sh
tx pull -a
```
This syncs updated .po files into:
```locales/<lang>/LC_MESSAGES/
```
## 📥 Manual Uploads via Transifex Web UI

If `.po` files were uploaded directly via the Transifex dashboard:

- ✅ Verify that each resource appears under the correct language
- ✅ Confirm language settings and translation completion status
- ✅ Pull those files to your local repo:

```sh
tx pull -l <language-code>
```
This ensures your local .po files match the ones stored on Transifex.


## Applying Translations
Once .po files are updated, compile them to .mo for use in the built documentation:

```sh
sphinx-build -D language=<language-code> -b html DISCOVER/ DISCOVER/_build/html

```
After compiling, rebuild the book to see the translations applied:

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

## ✅ Contributor Tips

- ✅ Include updated `.po` files in all translation-related commits  
- ✅ Use `generate_tx_config.py` when adding or removing `.po` files  
- ✅ Pull the latest translations from Transifex before compiling  
- ✅ Encourage community translators via the Transifex dashboard  


> Note: Contributors working on multilingual support should ensure .po file updates are included in commits.
