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


## Syncing with Transifex

We use Transifex as our translation service for the Cookbook, in order to collaborate on translations via Transifex, follow these steps:

### Step 1: Install the Transifex CLI

Download the latest Go-based CLI from the [Transifex CLI releases](https://github.com/transifex/cli/releases).

Place the binary in a folder like ```C:\tx-cli``` and add it to your system’s PATH.

Verify installation:
```sh
tx --version
```
Expected output:
```
TX CLient, version=1.6.x
```

### Step 2: Authenticate with Transifex

Create a ```.transifexrc``` file in your home directory ```(C:\Users\<yourname>\)``` with:

```python
[https://www.transifex.com]
rest_hostname = https://rest.api.transifex.com
token = 1/your_api_token_here
```
Get your token from [Transifex Account Settings](https://app.transifex.com/user/settings/api/).


### Step 3: Configure ```.tx/config```
This file lives in the root of the project and maps source files to Transifex resources.

```python
[main]
host = https://www.transifex.com
source_lang = en

[o:numfocus:p:DISCOVER-Cookbook:r:01_about]
source_file = locales/en/LC_MESSAGES/01_about.po
file_filter = locales/<lang>/LC_MESSAGES/01_about.po
type = PO
```

### Step 4: Push Source Files
To upload updated source files to Transifex:
```
tx push -s
```

To push translation files:
```
tx push -t
```

### Step 5: Pull Translations
To download all available translations:
```
tx pull -a
```

### Optional: Add Multiple Resources

To register all .po files under locales/en/LC_MESSAGES:
```
Get-ChildItem -Path locales/en/LC_MESSAGES -Filter *.po | ForEach-Object {
    $filename = $_.Name -replace '\.po$', ''
    $sourcePath = "locales/en/LC_MESSAGES/$($filename).po"
    $fileFilter = "locales/<lang>/LC_MESSAGES/$($filename).po"

    & "tx" add `
        --organization numfocus `
        --project DISCOVER-Cookbook `
        --resource $filename `
        --file-filter $fileFilter `
        --type PO `
        "$sourcePath"
}
```

## Tips:

- Always use forward slashes (/) in paths for compatibility.
- Run ```tx status``` to check resource sync.
- Use ```tx config discovery``` to auto-detect new files.

### Need help? Reach out to the maintainers or open an issue!
