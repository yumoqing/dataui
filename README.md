# dataui
A set of tools which auto generates frontend ui and backend data operation for data in table in database.

## crud
crud module generates crud UI for data in table in database.
base on a description json file, this module wll generate code by a parameter:
* browser: genrates the data browser UI
* filter: generates the filter condition input UI
* add: generates the new data input UI
* edit: generates the data modify UI
* remove: generates the delete data UI
* choose: browser data for choose, has filter UI.
* insert:generates the new data insert backend script;
* update:generates the update data backend script
* select:generates the query data backend script
* delete:generates the delete data backend script

## tree
tree module generates tree UI for hierarchy data in table in database.

a plugin for gadget webserver, it generates data browser 
