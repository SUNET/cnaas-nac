CSV Import / Export
===================

CNaaS NAC can export and import users in CSV format. Both import and
export can either be done from the API or through the web-interface.

Export
------

To export the database as a CSV-file simply press the fourth button in
the button bar (the one with an old faschined discette as icon) and
the whole database should be exported in CSV format and downloaded.

Import
------

Import is done in the same manner as export. Click the upload button
(the third button in the interface) and pick the CSV file on disk you want to upload.

Once the file is uploaded reload the UI and the new users should be
visible.

The format of the CSV files which can be uploaded should look like this::

  Username,Password,Active (true or false),VLAN (name or number),nas_identifier (can be left empty),nas_port_id (can be left empty),nas_ip_address (can be left empty),calling_station_id ,called_station_id,comment,reason,access start,access stop

The fields are:

- Username (for MAB this should be a MAC address)
- Password (for MAB this should be the same as the username)
- Active, whether the user should be active or not. Can be true or false.
- VLAN, which VLAN number or name the user should be assigned to.
- NAS identifier, name of the NAS. Can be left empty.
- NAS port ID, the NAS port (for example ethernet1). Can be left empty.
- NAS IP address, can be left empty.
- Calling station ID is the MAC address of the calling station.
- Called station, MAC address of the called station.
- Comment can be an arbitrary comment.
- Reason should be left empty.
- Access start is the time when the user should become active, can be left empty or set to a time in the format Y-m-d H-M (2023-01-01 01:00
- Access stop is the time when the user should be disabled, same format as access start.

An example CSV file can look like this::
  
  username,password,true,vlan,nas,ethernet1,1.2.3.4,aa:bb:cc:dd:ee:ff,ff:ee:dd:cc:bb:aa,comment,reason,2023-03-14 23:00,2023-03-20 01:00
