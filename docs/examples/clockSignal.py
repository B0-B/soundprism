from soundprism.signal import *

# create a normalized pulse with 50Hz period and 10% width
t = time.line(0.5)
signal = generator.clock(frequency=50, t=t, width=0.1)
plot(signal)