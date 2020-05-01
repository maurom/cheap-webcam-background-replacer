Poor man's Webcam Background Replacer
=====================================

Tired of your old and scruffy office wallpaper?

Wanna look just like those exemplar business men streaming from paradise landscapes?

Well, this won't cut it, but it is the most cheap and hackish way to replace the wall in your back with another image or video.

### Requirements

    apt install dkms linux-headers-`uname -r` \
        python3-numpy python3-opencv \
        v4l2loopback-dkms v4l2loopback-utils

but any virtualenv with those packages will do

### How to use it?

    dkms install v4l2loopback/0.12.4   # just to build and install that module

    modprobe v4l2loopback devices=1 video_nr=20 card_label="Fake Webcam" exclusive_caps=1

Now move away from the camera and execute (or run, but if you run, you will never be on the camera again)

    ./main.py --bg backgrounds/office.mp4 --output /dev/video20

Wait until the "Learning... nn" message stops appearing.

Then start any webcam or videoconference software you like and select the "Fake Webcam".

You can test v4l2loopback at any time using `mpv` or `vlc` as in

    mpv av://v4l2:/dev/video20

    vlc v4l2:///dev/video20

### Usage

```
usage: main.py [-h] [--background BACKGROUND] [--shadow] [--hologram]
               [--input INPUT] [--output OUTPUT] [--debug]

Replace webcam background with a static image or video.

optional arguments:
  -h, --help            show this help message and exit
  --background BACKGROUND, --bg BACKGROUND
                        image or video which will be used as background
  --shadow              adds shadow effect
  --hologram            adds hologram effect
  --input INPUT         input video device (webcam)
  --output OUTPUT       output video device (optional pyfake device)
  --debug
```

Please excuse the brevity. I'm really in a hurry.


## MOre backgrounds

- [ZoomerBackgrounds - Video calling in style.](https://zoomerbackgrounds.com/)
- [Funny zoom backgrounds - To make the meetings bearable](https://funnyzoombackgrounds.com/)
- [Zoom Backgrounds for work](https://www.reddit.com/r/zoombackgrounds/)
- [Pixabay Videos](https://pixabay.com/videos/)
- [Zoom backgrounds in UnSplash](https://unsplash.com/collections/1887152/zoom-backgrounds)

---

- Mauro A. Meloni (com.gmail@maumeloni)

