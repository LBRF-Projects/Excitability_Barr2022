instructions = {}

instructions['intro'] = [
    "Welcome to the motor imagery training task!",
    "",
    "We will begin with an introduction to motor imagery.",
    "Please close your eyes and press the return key to begin."
]

instructions['mi_training'] = [
    "Welcome to the motor imagery training task.",
    "",
    "Your task is to imagine yourself pressing each button following the cue.",
    "When you are ready to begin, please close your eyes and press the return key."
]

instructions['pp_testing'] = [
    "Block complete!",
    "Your next task is the physical performance block.",
    "You will hear the same cues as before",
    "but this time please respond as quickly as you can by pressing the corresponding key.",
    "Please close your eyes and press the return key to begin."
]

instructions['done'] = [
    "You're all done this task!",
    "Please alert the person conducting this experiment."
]


recall_replicate = (
    "try to replicate this sequence\n"
    "as many times as you can using the keys 1-4 for 20 seconds."
)
recall_avoid = (
    "try to avoid this sequence\n"
    "while randomly pressing the keys 1-4 for 20 seconds."
)
recall_suffix = [
    "It is okay if you you do not feel that there was a repeating sequence!",
    "Just try your best and go as quickly as you can!",
    "You will not hear any cues - press the return key to begin."
]


def get_instructions(order=1):

    # Order 1: replicate -> avoid
    if order == 1:
        recall1 = recall_replicate
        recall2 = recall_avoid
    # Order 2: avoid -> replicate
    elif order == 2:
        recall1 = recall_avoid
        recall2 = recall_replicate

    instructions['recall1'] = [
        "During the task, there may have been a sequence that repeated.",
        "Your next task is to " + recall1,
    ] + recall_suffix

    instructions['recall2'] = [
        "You're almost done!\n"
        "Your last task is to " + recall2,
    ] + recall_suffix

    return instructions
