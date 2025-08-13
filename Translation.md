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


> Note: Contributors working on multilingual support should ensure .po file updates are included in commits.


## Translation Workflow with Transifex

We use Transifex to manage translations for the DISCOVER Cookbook. This guide outlines when and how to interact with Transifex during development. You likely won’t need every step each time—focus on the ones relevant to your task.

### Step 1: Installing the Transifex CLI

Transifex provides a Go-based CLI for syncing translation files. Follow the (official installation instructions)[https://developers.transifex.com/docs/cli] for your operating system.


Verify installation:
```sh
tx --version
```
Expected output:
```
TX CLient, version=1.6.x
```

### Step 2: Authenticate with Transifex

To authenticate, create a ```.transifexrc``` file in your home directory. Refer to the [official authentication guide](https://developers.transifex.com/reference/api-authentication) for details.


Get your token from [Transifex Account Settings](https://app.transifex.com/user/settings/api/).


### Step 3: Updating ```.tx/config```

The ```.tx/config``` file maps source files to Transifex resources. You’ll only need to modify this when:

- Adding a new chapter or page to the Cookbook
- Removing or renaming existing translation files

Use the CLI to register new resources:
```
tx add \
  --organization numfocus \
  --project DISCOVER-Cookbook \
  --resource <resource_name> \
  --file-filter locales/<lang>/LC_MESSAGES/<filename>.po \
  --type PO \
  locales/en/LC_MESSAGES/<filename>.po
```

Refer to the [Transifex CLI reference](https://developers.transifex.com/docs/cli) for more information.


### Step 4: Pushing Source and Translation Files

After updating content or adding new chapters:
- Regenerate ```.po``` files using ```sphinx-gettext``` and ```sphinx-intl```.
- Open a PR with the updated files.
- Push to Transifex:
```
tx push -s -t
```

This uploads both source and translation files.

### Step 5: Pulling Translations
To fetch updated translations from Transifex (done manually before publishing):
```
tx pull -a
```

### Optional: Add Multiple Resources

To register all .po files refer to [guide](https://developers.transifex.com/docs/cli).


