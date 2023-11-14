# Playing Pretend with Planning and LLMs
Imaginative Agents using Large Language Models to Plan Grand Adventures Grounded in the Real World 

Currently only works with the OpenAI API

## Setup

For running the game demo, you must first clone the repo and create an Python 3 environment >= 3.10. We suggest creating a `conda` or `venv`. In the root directory of this project and with your Python environment active, download the requirements:

```pip install -r requirements.txt```

Then install the pretender module:

```pip install -e .```

## Alfworld server

1. Setup a new conda environment specifically for running the server, and install requirements.txt in alfworld_server

2. Setup alfworld within alfworld_server

3. Export the server directory to the Python Path:

```bash
export PYTHONPATH=$PYTHONPATH:<your-path-to-playingpretend>/alfworld_server
```

4. Run the following command to start the server 

```python
python alfworld_server/manage.py runserver --noreload
```

To run the planner and execute a plan, then run the `client_example.py`. 

`client_example.py` shows a sample run of hitting an API from the alfworld server.

### API interface 
To add your OpenAI API key for running you can add a file `api_key.txt` to the directory `pretender/utils` or simply sent your machine environment variable `OPENAI_API_KEY` as your key.

## Usage

Sample Pretender agent script command - 
```python run_game.py```

Sample bruteforce agent script command - 
```python ./brute_force.py $ALFWORLD_DATA/json_2.1.1/valid_train/pick_and_place_simple-AlarmClock-None-Desk-307/trial_T20190907_072317_014092/
```

## Troubleshooting

### `AssertionError: Invalid DISPLAY :0 - cannot find X server with xdpyinfo`

This is because the DISPLAY value for your X-window is incorrectly set in `alfworld`. Find the correct one by installing `mesa-utils` with `sudo apt install mesa-utils`, and run the command `DISPLAY=:i glxgears` while incrementing `i` until a gears graphic pops up. This is the value of your X-window. Fix it by finding the file `alfworld/alfworld/gen/constants.py` and set `X_DISPLAY=i` where `i` is that glxgears value you found to work.

### `AttributeError: 'dict' object has no attribute 'actions'`
This error occurs when the environment in which the Pretender agent (like `client_example.py`) doesn't have the `alfworld_server` subdirectory in the PYTHONPATH. Check that this is true with `echo $PYTHONPATH` and add it to your PYTHONPATH with `export PYTHONPATH=$PYTHONPATH:<path-to-playingpretend>/alfworld_server/`.
