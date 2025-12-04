## BK7084 Computational Simulations

This repository contains the framework and some reference assignments for the course BK7084 Computational Simulations.

---
## Installation

To run the code you need a Python interpreter (version **3.10 or newer**).

We recommend [PyCharm](https://www.jetbrains.com/pycharm/), which is free for students, because it makes setup easier:
1. If you don't have it already, download and install the latest version of Python from [python.org](https://www.python.org/downloads/).
   - On Windows, check “Add Python to PATH” during installation.
   - On macOS/Linux, Python 3 may already be installed, but make sure it’s at least 3.10.
2. Open this repository in PyCharm. (File --> Open)
3. When prompted, create a new **virtual environment** (venv). PyCharm will guide you through this.
4. Install dependencies by opening the console in PyCharm (press ctrl twice, or right-click the root folder -> Open In -> Terminal) and running:
    ```bash
       pip install -r requirements.txt
    ```

Alternatively, you can create the virtual environment manually, and use another code editor like Visual Studio Code. 
You do need a recent installation of Python and the requirements either way.

## Running Code

You can now run a python file using the console: ``python assignments/1_transformations.py`` (This assumes the console is currently open in the root folder of this project).

Alternatively, you can press the "start button" in PyCharm. This is both in the top right of the screen (here you also select what file to run), or in a python file itself, located next to a piece of code that looks as follows:

```py
if __name__ == "__main__":
    run_code_here()
```

## Tips 

- If imports like ``import framework`` fail, check that you are running from the project root.
    - Alternatively, in PyCharm, mark the root folder as Sources Root (right‑click -> Mark Directory as -> Sources Root). This ensures ``framework`` is recognized as a package.
- If other imports fail, check that you installed all required packages listed in requirements.txt
- When you create work on your own project, put all the files in root/project. You can start by extending the simple ``main.py`` script