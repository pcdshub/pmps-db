# PMPS

## Setup
### Dependencies
- bootstrap(internet access unless we download ui file and store locally/point to it)

### DB Setup
1. Run `touch pmps.db` in `pmps-db` directory

2. In `base.py`, change the engine variable to the correct db path:

```python
engine = create_engine("sqlite:////path/to/db/here/pmps-db/pmps.db")
```

3. Run `python start.py -c` to create tables

*Note: You can delete and recreate tables at any time with `python start.py -r`

### Other Setup
4. Run `mkdir export` in `pmps-db` directory

This is the folder where the exported plc data files will be located. If needed, this file path can be changed in the `export_by_plc()` function in the `db_connector.py` file.  

## Running
Run the Application from the Top Level Directory with:

`flask run`
