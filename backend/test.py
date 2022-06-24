import numpy as np
from time import sleep
from sound import *

# create a tone generator
gen = lambda f,t: combine(generator.sine(f, t), generator.saw(f, t), mode="multiply")

# initialize the piano and apply the generator
piano = keyBoard()
piano.applyGenerator(gen)

# tuning
delay = .07
level = 4
piano.volume = 0.2


# play a symphony
while True:
    try:
        for i in range(3):
            piano.play(f"G{level+2}",f"G{level+1}", duration=4*delay)
            piano.play(f"E{level+2}",f"E{level+1}", duration=2*delay)
            piano.play(f"G{level+2}",f"G{level+1}", duration=4*delay)
            piano.play(f"E{level+2}",f"E{level+1}", duration=2*delay)
            piano.play(f"B{level+2}",f"B{level+1}", duration=4*delay)
            piano.play(f"B{level+2}",f"B{level+1}", duration=4*delay)
            piano.play(f"A{level+2}",f"A{level+1}", duration=4*delay)
            piano.play(f"E{level+2}",f"E{level+1}", duration=2*delay)
        
        #piano.play(f"A{level+2}", duration=2*delay)
    except KeyboardInterrupt:
        break