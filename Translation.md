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

```sh
jupyter-book build DISCOVER
```

> Note: Contributors working on multilingual support should ensure .po file updates are included in commits.
