Get to the main directory containing the gentleman LLM code.
```bash
cd documents
```

Creates the virtual environment for the python script to run.
```bash
python -m venv .venv
```

Activates the virtual environment and installs the requirements.
```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.venv/Scripts/activate.ps1
pip install -r requirements.txt
```

Runs a basic call to the GentlemanLLM class.
```python
python main.py
```

Makes the api run and ready to receive requests.
```bash
uvicorn gentleman_request:app --reload
```

Exemple API call to the gentleman LLM API.
```python
python test_api.py
```

