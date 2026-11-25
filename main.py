from AppKit import *

app = NSApplication.sharedApplication()
app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
    NSMakeRect(500, 65, 900, 100), NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False)
# create the object for the window

win.setBackgroundColor_(NSColor.clearColor())  # set color background to transparent
win.setOpaque_(False) # set background to transparent
win.setLevel_(NSFloatingWindowLevel) # set how in front it is of other windows (make it in front of other app windows and behind menu bar)

label = NSTextField.labelWithString_("hello world") # make a text box
label.setFont_(NSFont.systemFontOfSize_(48)) # size text
label.setTextColor_(NSColor.whiteColor())   # color text
label.setFrame_(NSMakeRect(0, 0, 900, 100)) # box size
win.contentView().addSubview_(label)    # add the "label" to the 

win.makeKeyAndOrderFront_(None)
app.run()


# get the python file path  and replace it with the data song script 
script_path = Path(__file__).with_name("song_data.scpt")

def get_song():
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
    track, artist, pos, state = song_data.split('||')
    # every variable returned is a str so we need to convert
    pos = float(pos.replace(",","."))
        
    return track, artist, pos, state
    
    
        