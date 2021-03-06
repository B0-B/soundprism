<h1 align=center><strong> soundprism </strong></h1>

Sustaining signal & SFX generation and processing library with focus on VST instruments, music composition and sound design.


## Install

OS-independent install with `pip` package manager

```bash
pip install git+https://github.com/B0-B/soundprism.git@main
```

## Usage

Please visit the [docs](https://github.com/B0-B/soundprism/blob/main/docs/docs.md) for more information on usage and conventions.

### Signals

Load the signal library

```python
#!/usr/bin/env python3
from soundprism.signal import *
```

The general workspace is a time line of specific length, which is plugged into signal generators to bake a signal along the time line. All signal objects are `ndarray` objects which are fully compatible with numpy, scipy etc.


```python
# bake a C tone
time.sampleRate = 44100 # 44100 is default 
t = time.line(2)
signal = generator.sine(frequency=432, t)
```

combine two generators to form a custom generator or to modulate

```python
# first method
gen = lambda f,t: generator.sine(f, t) * generator.saw(1.5*f, t)

# second method
gen = lambda f,t: combine(generator.sine(f, t), generator.saw(1.5*f, t), mode="multiply")

# bake the signal
sig = gen(432, t)
plot(sig, show=True)
```
<img src="docs/images/sig2.png">

you can play the signal
```python
sound.play(signal, blocking=True)
```

It is possible to construct a pulse signal which is e.g. useful for brushless motor controllers.
The pulse width steers the thrust.

```python
# create a normalized pulse with 50Hz period and 10% width
t = time.line(0.5)
signal = generator.clock(frequency=50, t=t, width=0.1)
plot(signal)
```

<img src="docs/images/clock.png">

It is possible to apply this generator to a virtual keyboard
```python
from soundprism.vst import keyBoard

piano = keyBoard()
piano.applyGenerator(gen)

# play a single tone
piano.synth("C2#", duration=1, blocking=True)

# bind to your pc keyboard keys
piano.bindTonesToKeyboard()
```

also checkout the [examples](https://github.com/B0-B/soundprism/tree/main/docs/examples).