# Moonlapse Server

The server side for Moonlapse.

## Developer's Guide

The server runs as an event loop using the python [selectors](https://docs.python.org/3/library/selectors.html) package.

The protocol specification can be found in the [Moonlapse Shared](http://github.com/moonlapse-mud/shared) repository.

The server currently runs on 2 threads, one is the selector thread and one is the constant tick-timer. Once the tick-timer fires, it writes to a pipe which is being listened for on the selector thread, which avoids any race conditions.

### ProtoState

Every new connection is assigned a `Protocol` object which has a `ProtoState`. Every `Protocol` starts in the `EntryState`.

A `ProtoState` listens for specific packets and handles them differently.
