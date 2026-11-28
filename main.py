from AppKit import *
from pathlib import Path
from os import *
import subprocess
import requests
import re


# track_name/artist_name/duration (in int)
base_url = "https://lrclib.net/api/get"





app = NSApplication.sharedApplication()
app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

# create the object for the window
win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(500, 65, 900, 100), NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False)

# set the windows as an grabbable so you can place it anywhere you want !
win.setMovableByWindowBackground_(True)

win.setBackgroundColor_(NSColor.colorWithWhite_alpha_(0.0, 0.01))  # set color background to transparent
win.setOpaque_(False) # set background to transparent
win.setLevel_(NSFloatingWindowLevel) # set how in front it is of other windows (make it in front of other app windows and behind menu bar)

label = NSTextField.labelWithString_("hello world") # make a text box 
label.setFont_(NSFont.systemFontOfSize_(48)) # size text
label.setTextColor_(NSColor.whiteColor())   # color text
label.setFrame_(NSMakeRect(0, 0, 900, 100)) # box size
win.contentView().addSubview_(label)    # add the "label" to the 

win.makeKeyAndOrderFront_(None)


# to stack box
# NSStackView
# NSUserInterfaceLayoutOrientationVertical
#  = NSStackView.stackViewWithViews_([prev_label, curr_label, next_label])
# .setAlignment_(NSLayoutAttributeCenterX)

#app.run()


# get the python file path  and replace it with the data song script 
script_path = Path(__file__).resolve().with_name("song_data.scpt")

def get_song():
    song_info = []
    try:
        # check_output return des bytes donc besoin de text=True pour avoir format utf-8
        # dont forget to split to take off the \n at the end of every text returned
        song_data = subprocess.check_output(["osascript", script_path], text = True)
        # catch error in case the script return smt wrong or an error or so
    except subprocess.CalledProcessError:
        return None
    
    # security in case the player (applemusic) isnt started or bad output format
    if song_data == "stopped" or "||" not in song_data:
        return None
        
    # split the list given back
    track, artist, album, duration, pos, state = song_data.split('||')
    if "kPSP" in state:
        state = "playing"
    else :
        state = "paused"

        
    # every variable returned is a str so we need to convert
    pos = float(pos.replace(",","."))
    duration = float(duration.replace(",","."))
    
    song_info = track, artist, album, duration, pos, state
    
    return song_info
#print(get_song())



song = get_song()

if song == None:
    raise ValueError

#      [track_name, artist_name, album_name, duration]
keys = {"track_name": '', "artist_name": '', "album_name": '', "duration": ''}

print(song)
params = dict(zip(keys, song[:4]))

#print("\n\nparameters",params)
res = requests.get(base_url, params = params)
data = res.json()

lyrics = data.get("syncedLyrics")
#print(lyrics)


"""
For regex:
    ^   : for start of the text
    \d  : for decimal numbers so 0-9
    {X} : for numbers of times it should be written
    $   : for end of the text
    ()  : for what will be 'examined'
    []  : for matching the character inside
    +   : for one or more times
    ?   : for matching
    \b  : for starting at numbers/words
"""

    # start at a number, look for minutes first, include the : then look for seconds/millis
time_exp = re.compile(r"\b[0-20]\d:[0-5]\d(?:\.\d{2})?\b")



# need to convert lrc times to system player time
def lrc_to_time(timestamp) -> float:
    minutes, seconds = timestamp.split(":")
    return int(minutes) * 60 + float(seconds)

#print(lrc_to_time(time))

# to get the position and not other info
actual_time = song[4]

previous_lyrics = None
def match_lyrics(lyrics, actual_time):
    
    for line in lyrics.splitlines():
        # match is the regex to look for the expression we need in a line
        match = time_exp.search(line)

        if match :
            time = match.group()
            if actual_time >= lrc_to_time(time):
                clean_lyric = line.replace(f"[{time}]","")
            #print(clean_lyric)
        current_lyric = clean_lyric
        #print(time)
    return current_lyric


#print(match_lyrics(lyrics, actual_time))


def make_lyrics(lyric, size = 48):
    
    label = NSTextField.labelWithString_(lyric) # include text into the box
    label.setFont_(NSFont.systemFontOfSize_(size)) # size text
    label.setTextColor_(NSColor.whiteColor())   # color text
    label.setAlignment_(NSTextAlignmentCenter)  # align text
    return label

"""
prev_lyric = None
curr_lyric = None
next_lyric = None
stack = NSStackView.stackViewWithViews_([prev_label, curr_label, next_label])
stack.setOrientation_(NSUserInterfaceLayoutOrientationVertical)
stack.setAlignment_(NSLayoutAttributeCenterX)
stack.setSpacing_(20)  # Vertical gap between boxes
"""

# to stack box
# NSStackView
# NSUserInterfaceLayoutOrientationVertical
#  = NSStackView.stackViewWithViews_([prev_label, curr_label, next_label])
# .setAlignment_(NSLayoutAttributeCenterX)

win.makeKeyAndOrderFront_(None)
