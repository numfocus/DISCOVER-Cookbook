# Managing Translations

To support localization efforts, follow these steps to extract translatable strings and update translations.

> [!IMPORTANT]
> The target audience of this document are language coordinators. If you are interested
> in translating or are unsure about the meaning of "language coordinator" please read
> [the translator guide](./Translators_Guide.md) first.

## Generating `.pot` Files

To extract translatable text and generate `.pot` files, run:

```sh
sphinx-build -b gettext DISCOVER/ DISCOVER/_build/gettext
```
This will store extracted strings in .pot files inside DISCOVER/_build/gettext.

> [!NOTE]
> We have set [`gettext_uuid`](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-gettext_uuid) to `True` which can be slow.
> The cookbook isn't very large so it will generally not be relevant, but the linked sphinx docs have tips on accelerating that if relevant.

## Updating .po Files
To update existing translations, use the following command:

```sh
sphinx-intl update -p DISCOVER/_build/gettext -l <language-code>
```
Replace <language-code> with your target language (e.g., en, fr, de).

## Applying Translations
Once .po files are updated, and contain translations, you can rebuild the book to see the translations applied:

```sh
WEBSITE_LANGUAGE=<language-code> sphinx-build -b html DISCOVER/ DISCOVER/_build/html
```

### Opening the translated website preview

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


### Step 3: Updating ```.tx/config``` (optional)

The ```.tx/config``` file maps source files to Transifex resources.
The content on Transifex is only updated whenever a new release is published,
and `.tx/config` will only need updates if the files have changed.
Even if publishing a new release, if only the content within the files
has changed you can skip this step.

Use the CLI to register new resources:
```
tx add \
  --organization numfocus \
  --project DISCOVER-Cookbook \
  --resource <resource_name> \
  --file-filter locales/<lang>/LC_MESSAGES/<filename>.po \
  --type PO \
  DISCOVER/_build/gettext/<filename>.pot
```

Refer to the [Transifex CLI reference](https://developers.transifex.com/docs/cli) for more information.


### Step 4: Pushing Source and Translation Files

Perform the following steps only when a release is made:
- Regenerate `.pot` and `.po` files using ```sphinx-gettext``` and ```sphinx-intl```.
- Open a PR with the updated files.
- Push to Transifex:
```
tx push -s -t
```

This uploads both source and translation files to Transifex.

### Step 5: Pulling Translations
Whenever there have been significant updates to the translations on Transifex
these should be pulled locally and a PR opened against the latest published release.
What does "significant updates" means will depend on availability of
language coordinators and maintainers.

> [!IMPORTANT]
> Before fetching make sure you are in the `X.Y-translations` branch of the latest release.
> Otherwise the translations being pulled won't match the content and it will be more difficult
> to open a PR against the correct branch to get the translations deployed on the website.

To fetch updated translations from Transifex:
```
tx pull -a -m reviewed
```

### Optional: Add Multiple Resources

To add multiplt resorces, use [CLI](https://developers.transifex.com/docs/cli) setup.