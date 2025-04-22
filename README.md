File list:
- README.md - code documentation
- balatro.py - class definitions that handle running the simulation, Jokers can be enabled/disabled here, and discards can be set to any integer value
- balatro.ipynb - Jupyter notebook with 1 cell for importing balatro.py, and another cell that initializes class objects and triggers simulation of 10,000 Balatro runs
- requirements.txt - standard format for python packages required to be installed to run code

To run a simulation, please:
1. Create a Python virtual environment
    - For more info, see https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/
2. Install packages (in that environment)
    - ```pip install -r requirements.txt```
3. Ensure you are in the virtual environment on your IDE
4. (Optional) Configure Jokers, discards in balatro.py
    - Set Deck_Manager.discards = 3 or 0
    - Uncomment/Comment lines mentioning jokers in Deck_Manager.
    draw_cards_and_get_best_hand
    - Save any changes to file
    - Note: if there are any issues with updates not registering, restart your environment. First cell in balatro.ipynb should prevent that issue though
5. Run both cells in balatro.ipynb
    1. First cell imports class file with Deck_Manager and Run_Manager
    2. Second cell does r = 10,000 runs
6. Wait for a csv file to be generated from the second cell
    - This csv is for only one of many simulation configurations