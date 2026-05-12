# Setting Up DISCOVER-Cookbook Locally

This guide explains how to build and run the DISCOVER-Cookbook site on your local machine.

## Prerequisites

You will need either **Conda** or **pip** (Python 3.x) installed.

---

## Option 1: Using Conda

1. **Create the Conda environment**
   ```sh
   conda env create -f environment.yml
   ```

2. **Activate the environment**
   ```sh
   conda activate DISCOVER-Cookbook
   ```

3. **Build the book**
   ```sh
   sphinx-build -b html DISCOVER/ DISCOVER/_build/html
   ```

---

## Option 2: Using pip

1. **Create a virtual environment** (optional but recommended)
   ```sh
   python -m venv .venv
   ```

2. **Activate the virtual environment**
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Build the book**
   ```sh
   sphinx-build -b html DISCOVER/ DISCOVER/_build/html
   ```

---

## Viewing the Site Locally

After building, you can view the book in one of two ways:

### Option A: Using a local server (recommended)

```sh
python -m http.server 8000 --directory DISCOVER/_build/html/
```

Then open [`http://localhost:8000`](http://localhost:8000) in your browser.

### Option B: Opening the file directly

Navigate to:
```
DISCOVER/_build/html/index.html
```
and open it in your browser.

> **Note:** Make sure you rebuild the book after making any changes before viewing.
