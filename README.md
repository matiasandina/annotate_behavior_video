# annotate_behavior_video
This repository contains a very simple video annotator for animal behavior.


## Install

This software was built using python 3.4, but it has been tested in many other python distros so you should interpret this as 3.4+ (up to 3.11). You can get this software from the terminal using.

```
git clone https://github.com/matiasandina/annotate_behavior_video.git

```

To install dependencies.

```
pip3 install -r requirements.txt
```

You are advised to do this in a virtual environment. For example:

```
git clone https://github.com/matiasandina/annotate_behavior_video.git
cd annotate_behavior_video
python3 -m venv .annotator 
source .annotator/bin/activate
# some modules need numpy for install and you won't have it on a virtual environment
pip3 install numpy==1.22.0
pip3 install -r requirements.txt 
```

In windows, activating `venv` works like:

```
python3 -m venv .annotator 
.annotator\Scripts\activate
pip3 install -r requirements.txt
```

If you prefer conda, you can set up your virtual environment using it. 

```
conda create --name .annotator python
conda activate .annotator
pip3 install -r requirements.txt
```

## Usage

The main function is `annotator.py`, which uses 2 windows. The main window will contain most buttons used to control the video. The second window provides visual feedback for annotation.

### Main window

From this window you control the reproduction, type annotation (aka, type of behavior) and saving of data.

![main window](img/main_window.png)

### Ethogram window

From this window you can annotate the video and have a live ethogram representation of the annotations.

![ethogram](img/video_window.png)

### Example

Here's an example showing minimal functions of the main app. 

![](img/example_movie.gif)

### Self-Populated Behavior labels

By using a `config.yaml`, you can label different behaviors. For example, here's the file as apears in the repo

```
behaviors:
- not-specific
- sleep
- micro-arousal
- quiet-awake
- moving-awake
- eating-awake
```

Which will be read into the annotator and produce:


![](img/example_self_populated_buttons.png)

### HOTKEYS 

Hot keys have been added with the following bindings. 

```
self.key_options = ["a","s", "d", "f", "g", "h", "j", "k", "l"]
```

These will match the order of the behaviors on your config. Thus, following the example, "sleep" will be labeled when pressing "s".

## Next updates

Some updates will happen soon, this list contains the next things to be updated in order.

~~1. Allow for user to populate behavior categories at will on start-up.~~
~~1. Add function `on_key_press` (allow hotkeys for scoring).~~
~~1. Add ask before quit.~~
1. Add colors/style to matplotlib.
1. Make GUI look pretty

## Other functions

This repository contains some functions used to capture an LED blink on video. Future versions may or may not contain this functionality and documentation will not be developed for these.

## Contribute

This is a preliminary release. Please file issues to make this software work better.