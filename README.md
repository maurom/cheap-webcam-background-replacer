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

### Keys

While the app is running and the focus is on the output window, you can press the following keys to perform different commands:

- **b** or **B**: increase or decrease background blur level
- **d**: disable / enable background replacement
- **f**: advance video background by 5 sec
- **r**: re-train the background removal module
- **s**: show available background images / videos
- **1-9**: switch to background N
- **q**: quit the app


## MOre backgrounds

- [WindowSwap](http://window-swap.com/window) - [Sonali Ranjit on Vimeo](https://vimeo.com/user3419965)  
  A really interesting quarantine project by Sonali Ranjit and Vaishnav Balasubramaniam.
- [ZoomerBackgrounds - Video calling in style.](https://zoomerbackgrounds.com/)
- [Funny zoom backgrounds - To make the meetings bearable](https://funnyzoombackgrounds.com/)
- [Zoom Backgrounds for work](https://www.reddit.com/r/zoombackgrounds/)
- [Pixabay Videos](https://pixabay.com/videos/)
- [Zoom backgrounds in UnSplash](https://unsplash.com/collections/1887152/zoom-backgrounds)
- [Trabaje desde casa con estilo con los fondos virtuales GRATIS](https://www.shutterstock.com/es/discover/free-virtual-backgrounds)
- [Dartmouth Library Zoom Backgrounds](https://www.library.dartmouth.edu/library-zoom-backgrounds)
- [Library Backgrounds for Your Next Zoom Meeting](https://www.lapl.org/collections-resources/blogs/lapl/library-virtual-backgrounds-zoom)
- [All backgrounds for video calls](https://www.hellobackgrounds.com/backgrounds/#show-videos=true)
- [Den of Geek - Rick & Morty Zoom Backgrounds](https://www.denofgeek.com/tv/rick-and-morty-zoom-backgrounds/)
- [Den of Geek - Geeky Zoom Backgrounds](https://www.denofgeek.com/culture/best-geeky-zoom-backgrounds-virtual-meetings/)
- [Rick and Morty animated in the car](https://www.reddit.com/r/zoombackgrounds/comments/fuew3j/rick_and_morty_animated_in_the_car/)

---

- Mauro A. Meloni (com.gmail@maumeloni)

