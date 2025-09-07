Personal project only!
# RTL-SDR for moOdeaudio
This is my Frankenstein's monster. It allows me to add (US) local HD-Radio stations to moOdeaudio's Radio list.

* It uses nrsc5 by theori-io (https://github.com/theori-io/nrsc5) to decode HD-Radio signals from an RTL-SDR dongle attached to the Raspberry Pi.
* The signals are encoded by ffmpeg/libmp3lame and sent to Icecast.
* Icecast sets up a local stream that is interpreted by moOdeaudio as a webradio station.

Artist/Title are scraped from the nrsc5 stderr and sent to Icecast as metadata.
Adding stations to moOdeaudio uses a URI that tunes the frequency and multicast channel: http://127.0.0.1:8080/tune?freq=93.3&prog=0

It may take a couple clicks in moOdeaudio to tune a station. moOde tends to error out on the first click because the stream hasn't had a chance to start yet.

It also takes a few seconds to buffer and settle down, but it does work.
