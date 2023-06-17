form_defaults = {
    "nTran":"1",
    "nRate": ["0","1","10","120"],
    "aperture": ["None", "SL1K0", "SL2K0"],
    "nBeamClassRange": "000000000000000",
    "neVRange": "00000000000000000000000000000000"
}

#Pulled from Autosheet 1/19/23
access_groups = ["KFE", "RIX", "TMO"]
beamlines = {
    "SXR": ["KFE", "RIX", "TMO"], 
    "HXR":[]
    }
device_types = ["ATM", "B4C/Si MIRROR", "EXS YAG", "GAS ATTEN", "LASER INCOUPLING", "PPM", "REF LASER", "RTDS", "SCATTER SLIT", "WFS TARGET", "XPIM", "SPECTROMETER", "OTHER"]
plcs = ["plc-kfe-gatt", "plc-kfe-motion", "plc-kfe-rix-motion", "plc-rixs-optics", "plc-tmo-motion", "plc-tmo-optics"]

#Confluence
ev_ranges = {"HXR":[1,1.7,2.1,2.5,3.8,4,5,7,7.5,7.7,8.9,10,11.1,12,13,13.5,14,16.9,18,20,22,24,25,25.5,26,27,28,28.5,29,30,60,90],
 "SXR":[.1,.25,.27,.35,.4,.45,.48,.53,.68,.73,.85,1.1,1.15,1.25,1.45,1.5,1.55,1.65,1.7,1.75,1.82,1.85,2,2.2,2.5,2.8,3,3.15,3.5,4,5.3,7]}

#Form Titles and Variables
state_titles = ["ID","Name","Beamline", "nBC Range","nEV Range","NTran","NRate", "Aperture Name","Y Gap", "Y Center", "X Gap", "X Center", "Damage Limit", "Pulse Energy", "Notes", "Special", "Reactive Temp", "Reactive Pressure"]
state_fields = ['name','beamline', 'nBeamClassRange','neVRange','nTran','nRate','ap_name','ap_ygap', 'ap_ycenter', 'ap_xgap', 'ap_xcenter', 'damage_limit','pulse_energy','notes', 'special', 'reactive_temp', 'reactive_pressure']

history_titles = ["","ID","Timestamp","Name","Beamline", "nBC Range","nEV Range","NTran","NRate","Aperture Name","Y Gap", "Y Center", "X Gap", "X Center", "Damage Limit", "Pulse Energy", "Notes", "Special", "Reactive Temp", "Reactive Pressure"]
device_titles = ["Device ID/States", "Name", "PLC", "Device Type", "Beamline"]
