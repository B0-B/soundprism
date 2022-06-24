## Objects & Standards

`Units` (standard)


| Quantity | Unit |
|---|---|
| frequency/rate | Hz (1/s) |
| time | s (1/Hz) |
| phase angle | radiants (2π/360°) |

<br>



`Generators` (Object)

A generator is a signal-generating function which takes frequency and timeline as argument. 

                timeline
                    |
                    v
    generator --- bake ---> signal
                    ^
                    |
            arguments/parameters

`Signals` (Standard)

A signal is a persistent 1-D numpy array. Signals can be loaded
in baked form (from audio file) or can originate from a 
generator. 

<br>
    
