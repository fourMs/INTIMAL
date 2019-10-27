This folder contains the web interface and program that communicates with the bluetooth sensors and sends their data as OSC messages. 

To use web bluetooth and web osc
need to install osc-web\

Please go to https://github.com/automata/osc-web
and install it.

Has certain dependencies, node and socket
https://nodejs.org/en/

Installation:
$ git clone git://github.com/automata/osc-web.git
$ cd osc-web/
$ npm install

Using:
$ cd osc-web
$ node bridge.js

This starts osc-web and must run in the background.