# Moonlapse Server

The server side for Moonlapse.

## Developer's Guide

The server runs as an event loop using the python [selectors](https://docs.python.org/3/library/selectors.html) package.

The protocol specification can be found in the [Moonlapse Shared](http://github.com/moonlapse-mud/shared) repository.

The server currently runs on 2 threads, one is the selector thread and one is the constant tick-timer. Once the tick-timer fires, it writes to a pipe which is being listened for on the selector thread, which avoids any race conditions.

### ProtoState

Every new connection is assigned a `Protocol` object which has a `ProtoState`. Every `Protocol` starts in the `EntryState`.

A `ProtoState` listens for specific packets and handles them differently.


## Initialising DB and running locally

To initialise the database and run the server locally, you need to create a file in the base directory called `connectionstrings.json`.

In there, you can either create a debug local db which uses sqlite3 as the backend and a db file called `moonlapse.db` in the base directory.

A debug `connectionstrings.json` looks like:
```json
{
    "debug": true
}
```

while a production `connectionstrings.json` looks like:
```json
{
   "user": "MoonlapseAdmin",
   "password": "myPassword",
   "host": "localhost",
   "port": "5432",
   "database": "Moonlapse"
}
```

After the file is created, you then need to run the following commands in the base directory:
```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 loaddata.py
```

`loaddata.py` initialises all the static data in the database.

You can then run `python3 .` in the base directory to start the server.