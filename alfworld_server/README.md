To install the server specific python environment, create a Python 3.6 environment and add the requirements with 

```
pip install -r requirements.txt
```

afterwards, ensure that you install the `pretender` library as well:

```
cd ..
pip install -e .
```

To run the server
```python
python manage.py runserver --noreload
```

The --noreload option is important to avoid running two processes.
Starting the server starts alfworld, and we only want that to happen once.