# -*- coding: utf-8 -*-

__author__ = "Austin Hurst"

import random
from time import sleep
from time import perf_counter as time

import klibs
from klibs import P
from klibs.KLGraphics import fill, blit, flip
from klibs.KLEventQueue import pump, flush
from klibs.KLUserInterface import ui_request, any_key, key_pressed
from klibs.KLCommunication import message

from communication import get_trigger_port, get_tms_controller

WHITE = (255, 255, 255, 255)


class MEP_Baseline(klibs.Experiment):

    def setup(self):

        # Initialize TMS communication and trigger port
        magstim = get_tms_controller()
        trigger = get_trigger_port()
        trigger.add_codes(P.trigger_codes)

        # Confirm RMT and set TMS power to 120% RMT
        rmt = get_rmt_power(magstim)
        stim_power = int(round(rmt * 1.20))
        magstim.set_power(stim_power)
        
        # Perform MEP baseline collection
        pulse_delays = get_mep_baseline(magstim, trigger, pulses=10)
        print(pulse_delays)

        # Reset TMS power to RMT and exit
        try:
            magstim.set_power(rmt)
        except RuntimeError:
            print(" * NOTE: Error encountered resetting TMS power to RMT.")
        trigger.close()
        self.quit()



def get_rmt_power(magstim):
    rmt = magstim.get_power()
    txt = "Is {0}% the correct RMT for the participant? (Yes / No)"
    msg1 = message(txt.format(rmt), blit_txt = False)
    msg2 = message(
        "Please set the TMS power level to the correct RMT using the arrow keys,\n"
        "then press the [return] key to continue.",
        blit_txt = False, align = 'center'
    )

    rmt_confirmed = False
    flush()
    while not rmt_confirmed:
        # Draw RMT prompt to the screen
        fill()
        blit(msg1, 5, P.screen_c)
        flip()
        # Check for responses in input queue
        q = pump(True)
        if key_pressed('y', queue=q):
            rmt_confirmed = True
        elif key_pressed('n', queue=q):
            break

    # If TMS power level is incorrect, give chance to adjust w/ arrow keys
    rmt_temp = rmt
    while not rmt_confirmed:
        pwr_msg = message("Power level: {0}%".format(rmt_temp), blit_txt=False)
        fill()
        blit(msg2, 2, P.screen_c)
        blit(pwr_msg, 5, (P.screen_c[0], int(P.screen_y * 0.55)))
        flip()
        q = pump(True)
        if key_pressed('up', queue=q) and rmt_temp <= 100:
            rmt_temp += 1
        elif key_pressed('down', queue=q) and rmt_temp >= 0:
            rmt_temp -= 1
        elif key_pressed('return', queue=q):
            magstim.set_power(rmt_temp)
            sleep(0.1) # Give the magstim a break between commands
            rmt = magstim.get_power()
            rmt_confirmed = True

    return rmt


def get_mep_baseline(magstim, trigger, pulses=10, max_jitter=1.5):
    
    # Arm the TMS (assuming it's not already armed)
    magstim.arm()

    # Show starting message and wait for confirmation to start
    start_txt = (
        "Welcome to the MEP baseline collector!\n\n"
        "When collection starts, you will be stimulated a number of times by the "
        "TMS to measure your baseline muscle response. Please keep your arms relaxed "
        "until collection is complete.\n\n"
        "When you are relaxed and ready, please ask the experimenter to start the "
        "collection process."
    )
    wrap = int(P.screen_x * 0.75)
    start_msg = message(
        start_txt, align='center', wrap_width=wrap, blit_txt=False
    )
    fill()
    blit(start_msg, 5, P.screen_c)
    flip()

    # Wait for experimenter confirmation before starting baseline collection
    flush()
    while True:
        q = pump(True)
        if key_pressed("c", queue=q):
            break
    fill()
    flip()
    
    min_delay = 3.0
    pulse_delays = []
    for i in range(pulses):

        # Wait for 3s + jittered delay, then fire TMS
        interval = min_delay + random.uniform(0.0, max_jitter)
        onset = time()
        fire_delay = None
        while not fire_delay:
            ui_request()
            if time() > (onset + interval) and magstim.ready:
                fire_delay = time() - onset
                trigger.send('fire_tms')
                if P.development_mode:
                    fill(WHITE)
                    flip()
                    fill()
                    flip()

        # Print warning if fire delay was too short for TMS to re-arm
        if fire_delay > (interval + 0.1):
            msg = " * NOTE: TMS took {:.2f} sec to re-arm (interval: {:.2f}s)"
            print(msg.format(fire_delay, interval))

        pulse_delays.append(fire_delay)

    # Display end message and continue
    magstim.disarm()
    end_txt = "Baseline collection complete!\n\nPress any key to exit."
    flush()
    fill()
    message(end_txt, registration=5, location=P.screen_c, align='center')
    flip()
    any_key()

    return pulse_delays
        
        

