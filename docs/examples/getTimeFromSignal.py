#!/usr/bin/env python3
from soundprism.signal import *

# bake a C tone 
t = time.line(2)
signal = generator.sine(432, t)

# reconstruct the time array (in ms) from baked signal
t_reconstructed = time.lineFromSignal(signal)

print('Time reconstructed correctly:', equal(t, t_reconstructed))