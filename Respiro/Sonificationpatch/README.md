Sonification Patch
=======

This is a patch that sends and receives data from FLOW™ breathing sensors (<https://www.sweetzpot.com/flow>), locally and in-between distant locations (venues), and sonifies live the data.

This sonificationpatch folder contains the Max/MSP patch and required abstractions.

The program depends on an external library called the Sound Design Toolkit (SDT), which needs to be installed for Max/MSP from this link: <http://soundobject.org/SDT/>

The patch “respiro.maxpat" is the main patch which runs the other abstractions.

The patch works by first getting the data from the web application as OSC messages and then reading through them in blocks of 7 (newRealtimeInput.maxpat handles this), then the data is averaged and mapped to the three different sonification parts (wind, scraping, and drone (the drone synth is in abstraction dronesynth.maxpat)).
This produces the sound that is sent out from Max/MSP.

The communication between the other venues happens in the subpatch "p sendandreceive" which is where a user needs to input the correct IP addresses to send and receive data between venues.
