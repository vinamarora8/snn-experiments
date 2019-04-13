#! /usr/bin/python3.7m

import brian2 as b
from numpy import save
import matplotlib.pyplot as plt
print("\nLibraries loaded.")

b.start_scope()

t_max = 100*b.second
f = 10*b.Hz
filename = "/home/ven0m/code/btp/simple-0/stimulus.npy"

P = b.PoissonGroup(1, f)
M = b.SpikeMonitor(P)

def reporter(elapsed, complete, start, duration):
    print("\rSimulating... {}%".format(round(complete*100, 2)), end='', flush=True)
    
# run simulation
print("Simulating... ", end='', flush=True)
b.run(t_max, report=reporter, report_period=t_simul/100)
print("done")

print("Saving to '{}'... ".format(filename), end='', flush=True)
save(filename, [list(M.t), [0]*M.num_spikes])
print("done")

a = input("Show raster-plot? (y/n) ")
if a == 'y':
    plt.figure("float1")
    plt.plot(M.t, M.i, '.k')
    plt.show()
