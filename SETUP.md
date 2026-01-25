# How to Build and Run the Site Locally

Create a local python environment and install all the required dependencies using the following commands (either with conda or pip)

## If Using Conda
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
sphinx-build -b html DISCOVER/ DISCOVER/_build/html
```

## If Using pip
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
sphinx-build -b html DISCOVER/ DISCOVER/_build/html
```

## View Locally  
After building, you can view the book in one of the following ways:  

### **Option 1: Using a Local Server**  
Run the following command to start a local server:  
```sh
python -m http.server 8000 --directory DISCOVER/_build/html/
```
Then, open [`http://localhost:8000`](http://localhost:8000) in your browser.  

### **Option 2: Opening the File Directly**  
Alternatively, you can open the book directly by navigating to:  
```
DISCOVER/_build/html/index.html
```
and opening it in your browser.  

> **Note:** Make sure you have built the book again before accessing it.
