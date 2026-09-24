# How to Build and Run the Site Locally

This guide walks you through setting up a local development environment and building the DISCOVER Cookbook locally.

## Prerequisites

Ensure you have Python installed on your system, along with either:
- **Conda** (Miniconda / Anaconda), or
- **pip** and `venv` (standard Python package installer)

---

## Setup Instructions

Create a local Python environment and install all the required dependencies using either Conda or pip:

### If Using Conda

1. **Create the Conda Environment:**
   ```sh
   conda env create -f environment.yml
   ```

2. **Activate the Conda Environment:**
   ```sh
   conda activate DISCOVER-Cookbook
   ```

3. **Build the Jupyter Book:**
   ```sh
   sphinx-build -b html DISCOVER/ DISCOVER/_build/html
   ```

---

### If Using pip

1. **Create a Virtual Environment (optional):**
   ```sh
   python -m venv .venv
   ```

2. **Activate the Virtual Environment (optional):**
   - **On Windows:**
     ```sh
     .venv\Scripts\activate
     ```
   - **On macOS/Linux:**
     ```sh
     source .venv/bin/activate
     ```

3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Build the Jupyter Book:**
   ```sh
   sphinx-build -b html DISCOVER/ DISCOVER/_build/html
   ```

---

## View Locally

After building, you can view the book in one of the following ways:

### Option 1: Using a Local Server
Run the following command to start a local web server:
```sh
python -m http.server 8000 --directory DISCOVER/_build/html/
```
Then, open [`http://localhost:8000`](http://localhost:8000) in your browser.

### Option 2: Opening the File Directly
Alternatively, you can open the generated book directly by navigating to:
```
DISCOVER/_build/html/index.html
```
and opening it in your web browser.

> **Note:** Make sure you rebuild the book after making changes to see the latest updates.
