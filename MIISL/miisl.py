viewingDistance = 100
stimDisplayWidth = 100

responseKeySet = {
    'r': {'one': 'v', 'two': 'c', 'three': 'x', 'four': 'z'},
    'l': {'one': 'm', 'two': ',', 'three': '.', 'four': '/'},
}
sequenceProbability = .72  # NOTE: Doesn't actually do anything?

numLearningBlocks = 4 # num of MI blocks
sequenceSubBlocksPerLearningBlock = 18 # repeated elements/block in MI
randomSubBlocksPerLearningBlock = 7 # random elements/block in MI
sequencesPerLearningBlock = sequenceSubBlocksPerLearningBlock + randomSubBlocksPerLearningBlock
learningWaitTime = 1.500 # time in between keys

numRecallBlockResponses = 30

numTestingBlocks = 1 # num of PP blocks
sequenceSubBlocksPerTestingBlock = 10 # repeated elements/block in pp
randomSubBlocksPerTestingBlock = 10 # random elements/block in pp
testingWaitTime = 2.000 # why different than learningWaitTime ?
feedbackDuration = 1.000


### Import required libraries ###

import os
import sys
import math #for trig and other math stuff
import time
import shutil
import random

import sdl2
import sdl2.ext

from _runtime.utils import Sound, DataFile, init_window
from _runtime.sequences import create_random_sequence, create_repeating_sequence
from _runtime.communication import get_tms_controller, get_trigger_port
from instructions import get_instructions


# Initialize paths
data_dir = "_Data"
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

sound_dir = os.path.join("_Resources", "Sounds")
fontpath = os.path.join("_Resources", "DejaVuSans.ttf")


# Column names/orders for data files

# NOTE: multi_resp almost never happens (two keys pressed same frame),
#       merge with feedback_resp?
data_header = [
    'id', 'order', 'created', 'sex', 'age', 'handedness', 'rmt',
    'phase', 'block', 'run', 'trial', 'run_type', 'tms_fire',
    'stim', 'response', 'rt', 'error', 'multi_resp', 'feedback_resp',
]
recall_header = ['id', 'type', 'num', 'response', 'rt']
sequence_header = ['id', 'num', 'seq', 'keyseq']


# Initialize connection with Magstim & LabJack
magstim = get_tms_controller()
trigger = get_trigger_port()
trigger.add_codes({
    'fire_tms': 17, # EMG pin 1 + TMS trigger on pin 5
})

# Initialize and create the experiment window
stimDisplay = init_window(fullscreen=True)
stimDisplaySurf = stimDisplay.get_surface()
stimDisplayRes = stimDisplay.size
stimDisplayWidthInDegrees = math.degrees(
    math.atan((stimDisplayWidth / 2.0) / viewingDistance) * 2
)
PPD = stimDisplayRes[0] / stimDisplayWidthInDegrees  # Pixels per degree

# Define colours for the experiment
white = sdl2.pixels.SDL_Color(r=255, g=255, b=255, a=255)
black = sdl2.pixels.SDL_Color(r=0, g=0, b=0, a=255)
grey = sdl2.pixels.SDL_Color(r=127, g=127, b=127, a=255)
lightGrey = sdl2.pixels.SDL_Color(r=200, g=200, b=200, a=255)

# Initialize font rendering
fontsize = '{0}px'.format(int(PPD * 0.6))
font = sdl2.ext.FontTTF(fontpath, fontsize, white)
font.add_style("grey", fontsize, color=lightGrey)

# Load all audio clips for the experiment
intro_audio = Sound(os.path.join(sound_dir, "MIFamMono.mp3"))
stop_sound = Sound(os.path.join(sound_dir, "stop.mp3"))
done_sound = Sound(os.path.join(sound_dir, "done.mp3"))
stim_sounds = {}
for stim in ['one', 'two', 'three', 'four']:
    stim_sounds[stim] = Sound(os.path.join(sound_dir, stim + '.mp3'))

# Generate the repeated sequence for the participant
sequence = create_repeating_sequence()

# Generate list for TMS stimulation
total_sequences = numLearningBlocks * sequencesPerLearningBlock
num_true = 50
num_false = total_sequences - num_true
stim_true = [True for i in range(num_true)]
stim_false = [False for i in range(num_false)]
stim_sequence = stim_true + stim_false
random.shuffle(stim_sequence)


#define a function that will kill everything safely
def exitSafely():
    sdl2.ext.quit()
    sys.exit()

def flush():
    # Empties all pending events from the event queue
	sdl2.SDL_PumpEvents() 
	sdl2.SDL_FlushEvents(sdl2.SDL_FIRSTEVENT, sdl2.SDL_LASTEVENT)

def check_for_quit(queue):
    quitting = False
    for event in queue:
        # Quit on system quit events
        if event.type == sdl2.SDL_QUIT:
            quitting = True
            break
        # Quit on Esc or Ctrl-Q
        elif event.type == sdl2.SDL_KEYDOWN:
            k = event.key.keysym
            ctrl = k.mod & sdl2.KMOD_CTRL != 0
            if k.sym == sdl2.SDLK_ESCAPE or (ctrl and k.sym == sdl2.SDLK_q):
                quitting = True
                break
    if quitting:
        exitSafely()


#define a function that obtains the current time
def getTime():
    #return sdl2.SDL_GetPerformanceCounter()*1.0/sdl2.SDL_GetPerformanceFrequency()
    return sdl2.SDL_GetTicks()/1000.0

#define a function that waits for a given duration to pass
def simpleWait(duration):
    start = getTime()
    while getTime() < (start + duration):
        sdl2.SDL_PumpEvents()


#define a function that waits for a response
def waitForResponse(timeout=None,terminate=False):
    responses = []
    done = False
    while not done:
        if timeout!=None:
            if getTime()>timeout:
                done = True
        sdl2.SDL_PumpEvents()
        events = sdl2.ext.get_events()
        check_for_quit(events)
        for event in events:
            if event.type == sdl2.SDL_KEYDOWN:
                response = sdl2.SDL_GetKeyName(event.key.keysym.sym)
                response = sdl2.ext.compat.stringify(response).lower()
                responses.append([response,event.key.timestamp/1000.0])
                if terminate:
                    done = True
    return responses


#define a shortcut name for clearing the screen
def clearScreen(color):
    sdl2.ext.fill(stimDisplaySurf, color)


#define a function for formatting text for display
def drawText(myText, myFont, style='default', textWidth=.9):

    # If the text is empty, don't do anything
    if len(myText) == 0:
        return None

    # If the text is a list of strings, treat them as separate lines
    if isinstance(myText, list):
        myText = "\n".join(myText)

    # Actually render the text to an SDL surface
    screen_x, screen_y = stimDisplayRes
    width_px = int(screen_x * textWidth)
    surf = myFont.render_text(
        myText, style, width=width_px, line_h='150%', align='center'
    )

    # Draw the rendered text to the middle of the screen
    x = int(screen_x / 2.0 - surf.w / 2.0)
    y = int(screen_y / 2.0 - surf.h / 2.0)
    dest = sdl2.SDL_Rect(x, y, surf.w, surf.h)
    sdl2.SDL_BlitSurface(surf, None, stimDisplaySurf, dest)


#define a function that prints a message on the stimDisplay while looking for user input to continue. The function returns the total time it waited
def showMessage(myText,lockWait=False):
    messageViewingTimeStart = getTime()
    clearScreen(black)
    stimDisplay.refresh()
    clearScreen(black)
    drawText(myText, font, 'grey')
    simpleWait(0.500)
    stimDisplay.refresh()
    clearScreen(black)   
    if lockWait:
        response = None
        while response != 'return':
            response = waitForResponse(terminate=True)[0][0]
    else:
        response = waitForResponse(terminate=True)[0][0]
    stimDisplay.refresh()
    clearScreen(black)
    simpleWait(0.500)
    messageViewingTime = getTime() - messageViewingTimeStart
    return [response,messageViewingTime]


def getInput(getWhat):
    """Displays a prompt and collects text input, returning the result on enter.
    """
    # Clear screen and wait 0.5 seconds
    clearScreen(black)
    stimDisplay.refresh()
    simpleWait(0.500)

    # Draw input prompt to the screen
    getWhat = sdl2.ext.compat.utf8(getWhat)
    textInput = u''
    myText = getWhat + '\n' + textInput
    clearScreen(black)
    drawText(myText, font, 'grey')
    stimDisplay.refresh()

    # Enter input collection loop
    clearScreen(black)
    sdl2.SDL_StartTextInput()
    done = False
    while not done:
        sdl2.SDL_PumpEvents()
        events = sdl2.ext.get_events()
        check_for_quit(events)
        refresh = False
        for event in events:

            # Check for new text input
            if event.type == sdl2.SDL_TEXTINPUT:
                textInput += event.text.text.decode('utf-8')
                refresh = True

            # Check for backspace or enter keys
            elif event.type == sdl2.SDL_KEYDOWN:
                k = event.key.keysym
                if len(textInput):
                    if k.sym == sdl2.SDLK_BACKSPACE:
                        textInput = textInput[:-1]
                        refresh = True
                    elif k.sym in (sdl2.SDLK_KP_ENTER, sdl2.SDLK_RETURN):
                        done = True

        # If necessary, update the contents of the screen
        if refresh:
            myText = getWhat + '\n' + textInput
            clearScreen(black)
            drawText(myText, font, 'grey')
            stimDisplay.refresh()

    # Clear screen to black and return collected input
    clearScreen(black)
    stimDisplay.refresh()
    sdl2.SDL_StopTextInput()
    textInput = textInput.strip() # remove any trailing whitespace
    return textInput


# Draws random, filled rectangles on the passed surface
def draw_rects(surface, width, height):
    for k in range(2):
        # Create a set of four points for the edges of the rectangle.
        x, y = (0, 0)
        w, h = (width, height)
        # Draw the filled rect with the specified color on the surface.
        # fill(surface, color, ((x1, y1, x2, y2), (x3, y3, x4, y4), ...))
        #                        ^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^
        #                          first rect        second rect
        sdl2.ext.fill(surface, white, (x, y, w, h))
        stimDisplay.refresh()
        #clearScreen(white)
        simpleWait(0.500)
        sdl2.ext.fill(surface, black, (x, y, w, h))
        stimDisplay.refresh()
    #	simpleWait(0.100)


#define a function to run a testing block
def runBlock(blockType, datafile, subinfo):
    clearScreen(black)
    if blockType=='testing':
        sequencesPerThisBlock = sequenceSubBlocksPerTestingBlock
        randomsPerThisBlock = randomSubBlocksPerTestingBlock
    else:
        sequencesPerThisBlock = sequenceSubBlocksPerLearningBlock
        randomsPerThisBlock = randomSubBlocksPerLearningBlock
    subBlockList = []
    for i in range(sequencesPerThisBlock):
        subBlockList.append(['sequence', sequence])
    for i in range(randomsPerThisBlock):
        subBlockList.append(['random', create_random_sequence()])
    random.shuffle(subBlockList)
    subBlockNum = 0
    for subBlockType,subBlockStimuli in subBlockList:
        # Determine whether the sequence contains a TMS pulse & prepare accordingly
        stim = False
        if blockType == "learning":
            stim = stim_sequence.pop()
        # If TMS sequence, arm magstim and choose a random trial to fire on
        stim_trial = -1
        if stim:
            if not magstim.ready:
                magstim.arm()
            stim_trial = random.randint(2, 9)
        subBlockNum = subBlockNum + 1
        trialNum = 0
        for trialStim in subBlockStimuli:
            clearScreen(black)
            stimDisplay.refresh()
            trialNum = trialNum + 1
            sound = stim_sounds[trialStim]
            sound.play()
            startTime = getTime()
            if blockType=='testing':
                responseTimeoutTime = startTime+testingWaitTime
            else:
                responseTimeoutTime = startTime+learningWaitTime
            # If trial is a stim trial, make sure the TMS is armed and then fire
            if trialNum == stim_trial:
                if magstim.ready:
                    trigger.send('fire_tms')
            responses = waitForResponse(timeout=responseTimeoutTime,terminate=True)
            trialDoneTime = getTime()
            del sound
            response = 'NA'
            rt = 'NA'
            error = 'NA'
            feedbackText = ''
            feedbackResponse = 'FALSE'
            multiResponse = 'FALSE'
            if blockType=='testing':
                if len(responses)==0:
                    feedbackText = 'Miss!'
                elif len(responses)>1:
                    feedbackText = 'Respond only once!'
                    multiResponse = 'TRUE'
                else:
                    response = responses[0][0]
                    rt = responses[0][1]-startTime
                    if response==responseKeys[trialStim]:
                        feedbackText = str(int(rt*1000))
                        error = 'FALSE'
                    else:
                        feedbackText = 'XXX'
                        error = 'TRUE'
                    if response in responseKeys.values():
                        response = [key for key,value in responseKeys.items() if value==response][0]
                if (error=='TRUE') or (feedbackText=='Respond only once!') or (feedbackText=='Miss!'):
                    stop_sound.play()
                feedbackDoneTime = trialDoneTime+feedbackDuration
            else:
                if len(responses)>0:
                    stop_sound.play()
                    feedbackDoneTime = trialDoneTime+feedbackDuration
                    response = responses[0][0]
                    rt = responses[0][1]-startTime
                    feedbackText = "Don't respond!"
                else:
                    feedbackDoneTime = trialDoneTime
            #show feedback
            clearScreen(black)
            drawText(feedbackText, font)
            stimDisplay.refresh()
            responses = waitForResponse(timeout=feedbackDoneTime,terminate=True)
            if len(responses)>0:
                stop_sound.play()
                if feedbackText=='Miss!':
                    feedbackText = 'Too slow!'
                    response = responses[0][0]
                    rt = responses[0][1]-startTime
                else:
                    feedbackText = 'Respond only once!'
                    feedbackResponse = 'TRUE'
                clearScreen(black)
                drawText(feedbackText, font)
                stimDisplay.refresh()
                responses = waitForResponse(timeout=responses[0][1]+feedbackDuration,terminate=True)
            # Gather and write out data
            dat = subinfo.copy()
            dat.update({
                'block': blockNum + 1,
                'run': subBlockNum,
                'trial': trialNum,
                'phase': blockType,
                'run_type': subBlockType,
                'stim': trialStim,
                'response': response,
                'rt': rt,
                'tms_fire': trialNum == stim_trial,
                'error': error,
                'multi_resp': multiResponse,
                'feedback_resp': feedbackResponse,
            })
            datafile.write_row(dat)

            
def doRecall(datafile, subinfo):
    """Runs a recall (reproduce or avoid) block of the task."""
    responsesMade = 0
    lastTime = getTime()
    clearScreen(black)
    stimDisplay.refresh()
    for responseNum in range(numRecallBlockResponses):
        responses = waitForResponse(terminate=True)
        response = responses[0][0]
        rt = responses[0][1]-lastTime
        lastTime = responses[0][1]
        # Draw response and reaction time to screen
        clearScreen(black)
        drawText(' '.join(map(str,[responseNum+1, response, int(rt*1000)])), font)
        stimDisplay.refresh()
        # Gather and write out data
        dat = subinfo.copy()
        dat['num'] = responseNum + 1
        dat['response'] = response
        dat['rt'] = rt
        datafile.write_row(dat)

        
def getSubInfo():
    """Collect demographics info from the participant.
    """
    created = time.strftime("%Y-%m-%d %H:%M:%S") # Default R format (as.POSIXct)
    sid = getInput('ID (\'test\' to demo): ')
    order = getInput('Order (1 or 2): ')

    info = {'id': sid, 'order': order, 'created': created}
    if sid != 'test':
        info['sex'] = getInput('Sex (m or f): ')
        info['age'] = getInput('Age (2-digit number): ')
        info['handedness'] = getInput('Handedness (r or l): ')
    else:
        info['sex'] = 'test'
        info['age'] = 'test'
        info['handedness'] = 'r'

    return info


def get_rmt_power(tms):
    txt1 = "Is {0}% the correct RMT for the participant? (Yes / No)"
    txt2 = (
        "Please set the TMS power level to the participant's RMT,\n"
        "then press any key to continue."
    )
    rmt = tms.get_power()
    rmt_confirmed = False
    flush()
    while not rmt_confirmed:
        # Draw RMT prompt to the screen
        clearScreen(black)
        drawText(txt1.format(rmt), font, 'grey')
        stimDisplay.refresh()
        # Check for a response
        resp = waitForResponse(terminate=True)[0][0]
        if resp == 'y':
            rmt_confirmed = True
        elif resp == 'n':
            clearScreen(black)
            drawText(txt2, font, 'grey')
            stimDisplay.refresh()
            waitForResponse(terminate=True)
            rmt = tms.get_power()

    return rmt


def init_data(pid):
    # Create the data folder for the participant
    filebase = pid
    participant_dir = os.path.join(data_dir, filebase)
    if not os.path.exists(participant_dir):
        os.mkdir(participant_dir)

    # Make a copy of the code the experiment was run with
    code_path = os.path.join(participant_dir, filebase + "_code.py")
    shutil.copy(sys.argv[0], code_path)

    # Get the data output paths for the participant
    sequence_path = os.path.join(participant_dir, filebase + "_sequence.txt")
    rt_data_path = os.path.join(participant_dir, filebase + "_rt.txt")
    recall1_data_path = os.path.join(participant_dir, filebase + "_recall.txt")
    recall2_data_path = os.path.join(participant_dir, filebase + "_recall2.txt")

    # Create data output files for the participant
    datafiles = {
        'rt': DataFile(rt_data_path, data_header),
        'recall1': DataFile(recall1_data_path, recall_header),
        'recall2': DataFile(recall2_data_path, recall_header),
        'sequence': DataFile(sequence_path, sequence_header),
    }
    return datafiles



### Actually run the experiment ###

# Collect demographic/runtime info
subInfo = getSubInfo()
pid = subInfo['id']
order = int(subInfo['order'])
handedness = subInfo['handedness']
instructions = get_instructions(order)
responseKeys = responseKeySet[handedness]
keySequence = [responseKeys[stim] for stim in sequence]

# Get the RMT for the participant & set TMS power to 120%
rmt = get_rmt_power(magstim)
stim_power = int(round(rmt * 1.2))
subInfo['rmt'] = rmt
magstim.set_power(stim_power)

# Create data folder/files for the participant and write repeated sequence
datafiles = init_data(pid)
for i in range(len(sequence)):
    datafiles['sequence'].write_row({
        'id': pid,
        'num': i + 1,
        'seq': sequence[i],
        'keyseq': keySequence[i]
    })

# Show intro message and play tutorial audio
showMessage(instructions['intro'], lockWait=True)
draw_rects(stimDisplaySurf, 100, 100)
intro_audio.play()
while not intro_audio.doneYet():
    sdl2.SDL_PumpEvents() 
    events = sdl2.ext.get_events()
    check_for_quit(events)
    for event in events:
        if event.type == sdl2.SDL_KEYDOWN: # skips the audio
            if event.key.keysym.sym == sdl2.SDLK_DELETE:
                intro_audio.stop()
                break

# Perform MI training phase of the task
showMessage(instructions['mi_training'], lockWait=True) 
for blockNum in range(numLearningBlocks):
    draw_rects(stimDisplaySurf, 100, 100)
    runBlock('learning', datafiles['rt'], subInfo)
    stop_sound.play()
    if blockNum < (numLearningBlocks - 1):
        draw_rects(stimDisplaySurf, 100, 100)
        showMessage('Take a break!\nTo begin the next training block, press any key.')

# Perform physical testing phase of the task
showMessage(instructions['pp_testing'], lockWait=True)
for blockNum in range(numTestingBlocks):
    draw_rects(stimDisplaySurf, 100, 100)
    runBlock('testing', datafiles['rt'], subInfo)
    stop_sound.play()
    if blockNum < (numTestingBlocks- 1 ):
        draw_rects(stimDisplaySurf, 100, 100)
        showMessage('Take a break!\nTo resume, press any key.')

# Perform first recall block
showMessage(instructions['recall1'], lockWait=True)
recall_type = "avoid" if order == 2 else "replicate"
doRecall(datafiles['recall1'], {'id': pid, 'type': recall_type})
draw_rects(stimDisplaySurf, 100, 100)
stop_sound.play()

# Perform second recall block
showMessage(instructions['recall2'], lockWait=True)
recall_type = "replicate" if order == 2 else "avoid"
doRecall(datafiles['recall2'], {'id': pid, 'type': recall_type})
draw_rects(stimDisplaySurf, 100, 100)
stop_sound.play()

# Show completed message and exit the task
showMessage(instructions['done'], lockWait=True)
magstim.set_power(rmt) # reset TMS power level to RMT
exitSafely()