Contains all modules neccessary to communicate with the database.
Also includes the convenience structure networkModel. Changes made directly to
the graph in networkModel will not affect the database.

To insert a new object into the database, create corresponding entitymodel
(producer, information etc...) and call .save(). The globalNetwork is automatically
updated by this call.

To obtain the globalNetwork object call get_global_network from the globalNetwork module.
Forcing an update of the globalNetwork can be done by calling build_network_from_db.
