# Switch Squad HPC Log Visualization



This project processes historical PBS cluster snapshots to explore

computer resource usage over time.



## Tested development setup



- Operating system: Windows

- Terminal: PowerShell

- Python: 3.13.14

- Pandas: 3.0.6

- Package versions: recorded in requirements.txt



## Python version reasoning



Python 3.13 was used because it is already available on the development

machine, remains supported with security updates, and successfully

runs Pandas 3.0.6.



Reference: https://devguide.python.org/versions/



## Set up a working copy



Run these commands in PowerShell from the folder where you want

to keep the project:



```powershell

git clone https://github.com/chpc-tech-eval/switch-squad-hpc-log-viz.git

Set-Location .\switch-squad-hpc-log-viz

python --version

```



The setup documented here was tested with Python 3.13.14.



Create the project's Python environment and install its packages:



```powershell

python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

```



Check that Pandas loads:



```powershell

.\.venv\Scripts\python.exe -c "import pandas as pd; print('Pandas version:', pd.__version__)"

```



The expected Pandas version is 3.0.6.



## Dataset



The supplied dataset is stored in logs.zip.



## Team contributions



Each member should reproduce the setup on their own machine and

report any problems in GitHub Issue #1.



The .venv folder stays on each member's laptop. Its packages can

be recreated using requirements.txt.


