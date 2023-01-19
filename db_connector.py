
from base import Session, engine, Base

from models.devices import Devices
from models.states import States
from models.device_states import DeviceStates
from models.history import History

from flask import render_template, Blueprint, request, redirect, url_for, send_file

from sqlalchemy.exc import IntegrityError
from sqlalchemy import insert

import pprint, json, datetime, traceback

db_handler = Blueprint('db_handler', __name__, template_folder='templates')
state_titles = ["ID","Name","Beamline", "nBC Range","nEV Range","NTran","NRate", "Aperture Name","Y Gap", "Y Center", "X Gap", "X Center", "Damage Limit", "Pulse Energy", "Notes", "Special", "Reactive Temp", "Reactive Pressure"]
state_fields = ['name','beamline', 'nBeamClassRange','neVRange','nTran','nRate','ap_name','ap_ygap', 'ap_ycenter', 'ap_xgap', 'ap_xcenter', 'damage_limit','pulse_energy','notes', 'special', 'reactive_temp', 'reactive_pressure']

history_titles = ["","ID","Timestamp","Name","Beamline", "nBC Range","nEV Range","NTran","NRate","Aperture Name","Y Gap", "Y Center", "X Gap", "X Center", "Damage Limit", "Pulse Energy", "Notes", "Special", "Reactive Temp", "Reactive Pressure"]


device_titles = ["Device ID/States", "Name", "PLC", "Access Group"]


ev_ranges = {"HXR":[1,1.7,2.1,2.5,3.8,4,5,7,7.5,7.7,8.9,10,11.1,12,13,13.5,14,16.9,18,20,22,24,25,25.5,26,27,28,28.5,29,30,60,90],
 "SXR":[.1,.25,.27,.35,.4,.45,.48,.53,.68,.73,.85,1.1,1.15,1.25,1.45,1.5,1.55,1.65,1.7,1.75,1.82,1.85,2,2.2,2.5,2.8,3,3.15,3.5,4,5.3,7]}

@db_handler.route("/populate/", methods=["POST"])
def populate_base():
    """
    Endpoint for populating the database with data from a file
    """
    #Populate some base data to display in the table
    if not request.files:
        filename = "./data/combine.csv"
    else:
        filename = request.files['formFile']
    insert_autosheet(filename)
    return redirect(url_for('db_handler.device_info'))

@db_handler.route("/revert/", methods=["POST"])
def revert():
    """
    Endpoint for reverting history entry to be the 'current' state
    """
    #TODO: pass device ID through here 
    revert_id = request.form["history_radio"]
    session = Session()
    hist = session.query(History).filter(History.id==revert_id).one()
    session.close()

    sid = hist.state_id
    to_revert = hist.name,hist.beamline,hist.nBeamClassRange,hist.neVRange,hist.nTran,hist.nRate,hist.ap_name,hist.ap_ygap,hist.ap_ycenter,hist.ap_xgap,hist.ap_xcenter,hist.damage_limit,hist.pulse_energy,hist.notes,hist.special,hist.reactive_temp,hist.reactive_pressure
    new_state = update_state_db(sid, to_revert)

    state_content = format_state(new_state[0])
    if "device_name" in state_content:
        return render_template('state_helper.html', ev_ranges=ev_ranges,state_content=state_content, message="Reverted!")
    try:
        state_content["device_name"] = request.form["device_name"]
    except:
        print("Device ID not available to revert")
    return render_template('state_helper.html', ev_ranges=ev_ranges,state_content=state_content, message="Reverted!")

@db_handler.route("/export_page/", methods=["GET", "POST"])
def export_page():
    return render_template("landing.html", plcs=get_plcs())

def get_plcs():
    """
    Returns a list of all unique PLCS from the database
    """
    session = Session()
    plcs = session.query(Devices.plc).distinct().all()
    session.close()
    formatted_plcs = []
    for plc in plcs:
        #[('plc1',), ('plc2',)]
        temp = plc[0].split(',')
        formatted_plcs.append(temp[0])
    return formatted_plcs

@db_handler.route("/export_plc/", methods=["GET", "POST"])
def export_by_plc():
    """
    Builds a dictionary of one plc's device_ids and their state information and converts
    that to json.
    {PLC_Name:
        {Device_name:
            State_name:{
                state_information
            }
        }
    }
    """
    plc = request.form.get('plc_select')
    export_file = "export/exported_" + plc + "-" + str(datetime.datetime.now().isoformat()) + ".json"
    devices = get_devices_by_plc(plc)
    if not devices:
        return render_template("landing.html", message="Export Failed - No Device Information")
    export = get_export_data_by_device_ids(devices)
    plc_export = {plc:export}
    pprint.pprint(plc_export)
    with open(export_file, 'w') as f:
        f.write(json.dumps(plc_export))
    return send_file(export_file, as_attachment=True)

@db_handler.route("/export_all/", methods=["GET"])
def export_states_all():
    """
    Builds a dictionary of all device_ids and their state information and converts
    that to json.
    {Device_id:
        State_id:{
            state_information
        }
    }
    """
    export_file = "export/exported_" + str(datetime.datetime.now().isoformat()) + ".json"
    device_ids = get_all_device_ids()
    if not device_ids:
        return render_template("landing.html", message="Export Failed - No Device Information")
    export = get_export_data_by_device_ids(device_ids)
    with open(export_file, 'w') as f:
        f.write(json.dumps(export))
    return send_file(export_file, as_attachment=True)

def get_export_data_by_device_ids(devices):
    """
    Returns a dictionary of device data based off a list of device objects for exporting
    """
    export_dict = {}
    for device in devices:
        states = get_states_by_device_id(device.device_id)
        if not states:
            continue
        state_info = {}
        for state in states:
            clean_state = state.__dict__
            del clean_state['_sa_instance_state']
            state_info[state.name] = clean_state
        export_dict[device.name] = state_info
    return export_dict


@db_handler.route("/device_info/", methods=["GET", "POST"])
def device_info():
    """
    Endpoint for the device and state search/list page
    """
    devices = get_devices()
    return render_template('search.html', devices=devices)

@db_handler.route('/state_search_results/', methods=["POST"])
def state_search_results():
    state_string = request.form['state_name']
    session = Session()
    results = []
    if state_string == '':
        results = session.query(States)
        session.close()    
        return render_template('state_table.html', state_content=format_state(results))
    results = session.query(States).filter(States.name.contains(state_string))
    if not results:
        session.close()    
        return render_template('landing.html')
    session.close()
    return render_template('state_table.html', state_content=format_state(results))

@db_handler.route('/device_search_results/', methods=["POST"])
def device_search_results():
    dev_string = request.form['device_name']
    session = Session()
    if dev_string == '':
        results = session.query(Devices)
        session.close()    
        return render_template('all_devices.html', device_content=format_device(results))
    results = session.query(Devices).filter(Devices.name.contains(dev_string))
    if not results:
        session.close()    
        return render_template('all_devices.html', device_content=format_device(results))
    session.close()    
    return render_template('all_devices.html', device_content=format_device(results))

@db_handler.route("/states_by_group/", methods=["POST"])
def states_by_group():
    """
    Get a list of states for multiple devices of one group
    """
    search_string = request.form["dev_pref"] + "%_" + request.form["dev_type"]
    session = Session()
    results = session.query(Devices.device_id, Devices.name).filter(Devices.name.like(search_string)).all()
    session.close()
    devices = []
    states = []
    for device_id in results:
        new_states = get_states_by_device_id(device_id[0])
        #Check for no results from database
        if not new_states:
            continue
        states += new_states
        device_data = (list(device_id))
        count=0
        while count < len(new_states):
            devices.append(device_data)
            count +=1
    return render_template('state_table.html', state_content=format_state(states),devices=devices)


@db_handler.route("/update_state/", methods=["POST"])
def update_state():
    """
    Updates state information from the state table form
    """
    session = Session()
    s_id = request.form['s_id']
    device_name = request.form.get('device_select')
    if device_name == None:
        device_name = request.form['device_name']
    device_id = session.query(Devices.device_id).filter(Devices.name == device_name).one()
    orig_state = [request.form.get('s_name'), request.form['s_beam'], request.form['s_bcr'], request.form['s_nev'], request.form['s_nt'], request.form['s_nr'], request.form['s_as'], request.form['s_ayg'],request.form['s_ayc'],request.form['s_axg'],request.form['s_axc'],request.form['s_apn'], request.form['s_pen'], request.form['s_on'], request.form.get('s_sp'), request.form['s_rt'], request.form['s_rp']]
    if orig_state[14] == "special":
        orig_state[14] = True
    state = check_state(s_id)
    if state:
        state_info = update_state_db(s_id, orig_state)
    else:
        orig_state[0] = device_name + '-' + orig_state[0]
        state = add_new_state(session, orig_state[0], orig_state)
        state_info = check_state(state.id)
        if not state_info:
            session.close()
            return render_template('state_table.html', state_content=format_state(['','','']), message="Failed!")
        insert_device_states({device_id[0]: [state.id]}, session)
    session.close()
    return render_template('state_table.html', state_content=format_state(state_info), message="Saved!")

@db_handler.route("/add_device/", methods=["POST"])
def add_device():
    name = request.form['d_name']
    plc = request.form.get('plc_select')
    ag = request.form['d_ag']
    """    exists = check_device(name)
    if exists:
        return render_template('new_device.html', device_content=format_device((0,name, plc, ag)), msg="Device Name Already Exists")"""
    session = Session()
    try:
        session.execute(insert(Devices).values(name=name, plc=plc, access_group=ag))
        session.commit()
    except IntegrityError:
        print(traceback.format_exc())
        session.close()
        return render_template('new_device.html', device_content=format_device((0,name, plc, ag)), plcs=get_plcs(), msg="Device Name Already Exists")
    except:
        print(traceback.format_exc())
        session.close()
        return render_template('new_device.html', device_content=format_device((0,name, plc, ag)), plcs=get_plcs(), msg="Unable to Add Device")
    all_devices = session.query(Devices).all()
    session.close()
    return render_template('all_devices.html', device_content=format_device(all_devices))

def check_device(session, device_name):
    """
    From a device name, check if an entry exists in the database
    """
    device = session.query(Devices).filter(Devices.name==device_name).all()
    return device[0] if device else None

def check_state(sid):
    """
    From a state id, check if an entry exists in the database
    """
    session = Session()
    results = session.query(States).filter(States.id==sid).all()
    session.close()
    return results if results else None

def update_state_db(sid, state):
    """
    From a specific state id, updates a previously existing state in the database with new valueset
    """
    session = Session()
    to_update = {}
    counter=0
    for state_val in state:
        to_update[state_fields[counter]] = state_val
        counter+=1
    session.query(States).filter(States.id==sid).update(to_update)
    session.commit()
    
    #add entry into history table
    history = History(sid, *state)
    session.add(history)

    session.commit()

    state_info = session.query(States).filter(States.id==sid).all()
    session.close()

    return state_info

@db_handler.route("/device_states/", methods=["GET","POST"])
def device_states(device_id=None):
    """
    From a provided device id, get the related states from inside the database
    and provide them to the user for state selection
    """
    device_id = request.form['device_id']
    devices = get_devices()
    return render_template('search.html', device_id=device_id, devices=devices, device_states=get_dev_states_by_device_id(device_id))

@db_handler.route("/device_states_display/", methods=["GET","POST"])
def device_states_display(device_id=None):
    """
    From a provided device id, get the related states from inside the database
    and provide them to the user for state selection
    """
    if not device_id:
        device_id = request.args.get('device_id')
    states = get_states_by_device_id(device_id)
    state_content = format_state(states)
    if not states:
        state_content["device_name"] = get_device_name_from_id(device_id)
    return render_template('state_table.html', device_id=device_id, state_content=state_content)

@db_handler.route("/state_helper/", methods=["GET", "POST"])
def state_helper():
    """
    Endpoint for the more detailed single state view
    """
    state_id = request.args.get('state_id')
    state_info = get_state_by_id(state_id).__dict__
    return render_template('state_helper.html', ev_ranges=ev_ranges,state_content=format_state(state_info))

@db_handler.route("/single_state/", methods=["POST"])
def single_state():
    """
    Populates the generic multi-state table with information for one specific state
    """
    state_id = request.form['state_info']
    state_info = get_state_by_id(state_id)
    return render_template('state_table.html', state_content=format_state(state_info))  

@db_handler.route("/add_state/", methods=["POST", "GET"])
def add_state():
    """
    Opens the view to create a new state
    """
    state_info = ['','','']
    state_content=format_state(state_info)
    state_content["device_name"] = request.args.get("device_name")
    return render_template('state_helper.html', ev_ranges=ev_ranges,state_content=state_content, new=True, devices=get_device_names())  

@db_handler.route("/new_device/", methods=["POST", "GET"])
def new_device():
    """
    Opens the view to create a new device
    """
    device_info = ['','','']
    device_content=format_device(device_info)
    return render_template('new_device.html', device_content=device_content, plcs=get_plcs())  

@db_handler.route("/state_info/", methods=["POST"])
def state_info():
    """
    Populates state table page with all state information tied to a device
    """
    device_id = request.form["device_id"]
    states = get_states_by_device_id(device_id)
    if states:
        state_content=format_state(states) 
    else:
        state_content=format_state(['','',''])
    return render_template('state_table.html', state_content=state_content)

@db_handler.route("/state_history/", methods=["GET", "POST"])
def state_history():
    """
    Populates history table page with all history of one state
    """
    state_id = request.form["state_id"]
    state_content = {"titles":history_titles, "states":get_state_history(state_id), "device_name":request.form["device_name"]}
    return render_template('history_table.html', state_content=state_content)

def format_state(states):
    """
    Formats the state content for the UI.
    Includes fetching the device name and accessing the table column names
    """
    session = Session()
    if not states:
        print("ERROR: No States to Format")
        session.close()
        return {"titles":state_titles, "states":['','','']}
    try:
        if isinstance(states, list):
            device_name = session.query(
                Devices.name
                ).join(
                    DeviceStates
                ).filter(
                    DeviceStates.state_id==states[0].id
                ).one()
        elif isinstance(states, dict):
            device_name = session.query(
                Devices.name
                ).join(
                    DeviceStates
                ).filter(
                    DeviceStates.state_id==states['id']
                ).one()
        state_content = {"device_name":device_name[0], "titles":state_titles, "states":states}
    except:
        state_content = {"titles":state_titles, "states":states}
    session.close()
    return state_content

def format_device(devices):
    """
    Formats the device content for the UI
    """
    device_content = {"titles":device_titles, "devices":devices}
    return device_content

def get_states_by_device_id(device_id=None):
    """
    Returns all state data. If a device_id is included as a parameter, returns all
    state data for that device. Otherwise, it dumps all state data for all devices.
    """
    session = Session()
    states = []
    if not device_id:
        states = session.query(States).all()
    else:
        device_states = get_dev_states_by_device_id(device_id)
        if not device_states: return None
        for state_id in device_states:
            states.append(session.query(States).filter(States.id==state_id[0]).one())
    session.close()
    return states if states else None

def get_devices_by_plc(plc):
    """
    Get all devices by the given PLC name 
    """
    session = Session()
    devices = session.query(Devices).filter(Devices.plc==plc).all()
    session.close()
    return devices if devices else None

def get_state_history(state_id):
    """
    Gets all change history of a single state id
    """
    session = Session()
    state_info = session.query(History).filter(History.state_id==state_id).order_by(History.timestamp.desc()).all()
    session.close()
    return state_info if state_info else None

def get_state_by_id(state_id):
    """
    Gets state information from the database based off of the unique state id
    """
    session = Session()
    state_info = session.query(States).filter(States.id==state_id).all()
    session.close()
    return state_info[0]

def get_devices():
    """
    Gets a list of all device ids, names, and plcs from the database
    """
    session = Session()
    devices = session.query().with_entities(Devices.device_id, Devices.name, Devices.plc).all()
    session.close()
    return devices if devices else None

def get_device_name_from_id(device_id):
    session = Session()
    name = session.query(Devices.name).filter(Devices.device_id==device_id).one()
    session.close()
    return name[0] if name else None

def get_device_names():
    """
    Gets a list of all device names from the database
    """
    session = Session()
    devices = session.query(Devices.name).all()
    session.close()
    formatted_devices = []
    for dev in devices:
        formatted_devices.append(dev[0].split(',')[0])
    return formatted_devices

def get_all_device_ids():
    """
    Returns a list of all Device objects(with id field) in db
    """
    session = Session()
    device_ids = session.query(Devices.device_id).all()
    session.close()
    return device_ids if device_ids else None

def get_dev_states_by_device_id(device_id=None):
    """
    Get a list of all device state objects. 
    Inludes an optional device id parameter that limits results to those associated with the device id
    """
    session = Session()
    if device_id:
        device_states = session.query(DeviceStates.state_id).filter(DeviceStates.device_id==device_id).all()
    else:
        device_states = session.query(DeviceStates.state_id).all()
    session.close()
    return device_states if device_states else None

def insert_autosheet(filename):
    """
    Parses and inserts all data from a csv into the database
    """
    session = Session()
    device_states = {}
    file_content = filename.read().decode('utf-8')
    for line in file_content.split('\n'):
        if (not line) or (line == '') or (line[0]==","):
            continue
        commas = line.rstrip('\n').split(",")
        if commas[0]=="COMPONENT":
            continue
        #Remove "human readable" range from autosheet
        del commas[7]
        device = commas[0:4]
        #split out the PLC
        state = [commas[2]] + commas[4:]
        #If device does not exist yet in the db, create one
        dev = handle_device(session, device)
        #Something went wrong, bad line
        if not dev:
            continue
        state_name = dev.name + "-" + state[1].replace(" ", "").upper()
        state = handle_state(session, state_name, state)
        #Something went wrong, bad line
        if not state:
            continue
        device_states.setdefault(dev.device_id,[]).append(state.id)
    insert_device_states(device_states, session)
    session.commit()
    session.close()
    return

def handle_state(session, state_name, state):
    """
    Parses and adds state entry into the database in state and history tables. 
    
    params: state_name(str) - device_name-state_name
    Returns: State SQLAlchemy object
    """
    #Swap dashes with None, clear out empty elements/strings in list
    state = ['' if sub == '-' else sub for sub in state]
    state_obj = States(name=state_name,beamline=state[0],nBeamClassRange=state[3],neVRange=state[4],nTran=state[5],nRate=state[6],ap_name=state[7],ap_ygap=state[8],ap_ycenter=state[9],ap_xgap=state[10],ap_xcenter=state[11],damage_limit=state[12],pulse_energy=state[13],notes=state[14],special=None,reactive_temp=state[15],reactive_pressure=state[16])
    try:
        session.add(state_obj)
        session.commit()
    except IntegrityError:
        session.rollback()
        print("ERROR: State with Unique ID ", state_name, "already exists.")
        return
    except:
        session.rollback()
        print(traceback.format_exc())
        print("ERROR: Unable to Add State ", state_name)
        return
    insert_hist = (
        insert(History).
            values(state_id=state_obj.id,name=state_name,beamline=state[0],nBeamClassRange=state[3],neVRange=state[4],nTran=state[5],nRate=state[6],ap_name=state[7],ap_ygap=state[8],ap_ycenter=state[9],ap_xgap=state[10],ap_xcenter=state[11],damage_limit=state[12],pulse_energy=state[13],notes=state[14],special=None,reactive_temp=state[15],reactive_pressure=state[16])
        )
    session.execute(insert_hist)
    session.commit()
    return state_obj if state_obj else None

def add_new_state(session, state_name, state):
    """
    Adds a new state into the database. Called by the UI, so processess state string differently
    Returns: State SQLAlchemy object
    """
    state_obj = States(name=state_name,beamline=state[1],nBeamClassRange=state[2],neVRange=state[3],nTran=state[4],nRate=state[5],ap_name=state[6],ap_ygap=state[7],ap_ycenter=state[8],ap_xgap=state[9],ap_xcenter=state[10],damage_limit=state[11],pulse_energy=state[12],notes=state[13],special=state[14],reactive_temp=state[15],reactive_pressure=state[16])
    try:
        session.add(state_obj)
        session.commit()
    except IntegrityError:
        session.rollback()
        print("ERROR: State with Unique ID ", state_name, "already exists.")
        return
    except:
        session.rollback()
        print(traceback.format_exc())
        print("ERROR: Unable to Add State ", state_name)
        return
    insert_hist = (
        insert(History).
            values(state_id=state_obj.id,name=state_name,beamline=state[1],nBeamClassRange=state[2],neVRange=state[3],nTran=state[4],nRate=state[5],ap_name=state[6],ap_ygap=state[7],ap_ycenter=state[8],ap_xgap=state[9],ap_xcenter=state[10],damage_limit=state[11],pulse_energy=state[12],notes=state[13],special=state[14],reactive_temp=state[15],reactive_pressure=state[16])
    )
    session.execute(insert_hist)
    session.commit()
    return state_obj if state_obj else None

def handle_device(session, device):
    """
    Parses and adds a device entry into the database
    Returns: Device SQLAlchemy object
    """
    dev = check_device(session, device[0])
    if not dev:
        #Device Structure: name, plc, access_group, device_type
        insert_stmt = insert(Devices).values(name=device[0], plc=device[3], access_group=device[2], device_type=device[1])
        try:
            session.execute(insert_stmt)
            session.commit()
            dev = session.query(Devices).filter(Devices.name==device[0]).one()
        except IntegrityError:
            session.rollback()
            print("ERROR: Device with Unique ID ", device[0], "already exists.")
            return None
    return dev if dev else None

#This is the insert that was previously used for my old data format. See insert_autosheet for up to date data parsing
def insert_data(filename):
    """
    Parses and inserts all data from a csv into the database
    """
    session = Session()
    device_states = {}
    file_content = filename.read().decode('utf-8')
    for line in file_content.split('\n'):
        if not line or line == '':
            continue
        if line[0] == "#":
            continue
        commas = line.rstrip('\n').split(",")
        if commas[0].lower() == "device":
            dev_state = insert_device_and_states(commas[1:], session)
            if dev_state:
                device_states.update(dev_state)
        elif commas[0].lower() == "state":
            insert_state(commas[1:], session)
        else:
            print("ERROR: Unable to process line ", line)

    insert_device_states(device_states, session)
    session.commit()
    session.close()
    return

def insert_device_and_states(line, session):
    """
    Parses device data and state information and adds it into the database. 
    Returns state information per device
    """
    #device,id,name,plc,access_group,states
    dev_id = line[1]
    states = {dev_id:[]}
    #insert_stmt = insert(Devices).values(device_id=line[1], name=line[0], plc=line[2], access_group=line[3])
    insert_stmt = insert(Devices).values(name=line[0], plc=line[2], line_type=line[3], access_group=line[4])
    for field in line[4:]:
        if not field or field=="\r" or field=="":
            continue
        states[dev_id].append(field.strip('"'))
    try:
        session.execute(insert_stmt)
        session.commit()
    except IntegrityError:
        session.rollback()
        print("ERROR: Device with Unique ID ", line[1], "already exists.")
        return None
    except:
        session.rollback()
        print("ERROR: Unable to Add Device ", line[0])
        return None
    return states

#Also depreciated, only called in insert_data
def insert_state(line, session):
    #Name,ID,nBeamClassRange,neVRange,nTran,ap name,ygap,ycenter,xgap,xcenter,damage limit,pulse energy,other notes,special case,reactive temo,reactive pressure,,,,,,,,
    #Swap dashes with None, clear out empty elements/strings in list    
    #line = ['' if sub == '-' else sub for sub in line if sub != ""]
    line = ['' if sub == '-' else sub for sub in line]

    #Format Special Flag:
    if line[14] == '':
        line[14] = False
    insert_stmt = (
        insert(States).
        values(id=int(line[1]),name=line[0],beamline=line[2],nBeamClassRange=line[3],neVRange=line[4],nTran=line[5],ap_name=line[6],ap_ygap=line[7],ap_ycenter=line[8],ap_xgap=line[9],ap_xcenter=line[10],damage_limit=line[11],pulse_energy=line[12],notes=line[13],special=line[14],reactive_temp=line[15],reactive_pressure=line[16])
        )
    try:
        session.execute(insert_stmt)
        session.commit()
    except IntegrityError:
        session.rollback()
        print("ERROR: State with Unique ID ", line[1], "already exists.")
        return
    except:
        session.rollback()
        print(traceback.format_exc())
        print("ERROR: Unable to Add State ", line[0])
        return
    insert_hist = (
        insert(History).
        values(state_id=int(line[1]),name=line[0],beamline=line[2],nBeamClassRange=line[3],neVRange=line[4],nTran=line[5],ap_name=line[6],ap_ygap=line[7],ap_ycenter=line[8],ap_xgap=line[9],ap_xcenter=line[10],damage_limit=line[11],pulse_energy=line[12],notes=line[13],special=line[14],reactive_temp=line[15],reactive_pressure=line[16])
        )
    session.execute(insert_hist)
    session.commit()
    return

def insert_device_states(device_states, session):
    """
    Inserts a dictionary of device_states into the database.
    Params: device_states(dict) : {device_id:[state_id_1,state_id_2,...]}
    """
    for device in device_states.keys():
        for state in device_states[device]:
            device_state_row = DeviceStates(device, state)
            try:
                session.add(device_state_row)
                session.commit()
            except IntegrityError:
                session.rollback()
                print("ERROR: Device State with Unique ID ", state, "already exists.")
            except:
                session.rollback()
                print("ERROR: Unable to Add Device State ", state)
    return
