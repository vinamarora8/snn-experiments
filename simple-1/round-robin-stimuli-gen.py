#! /usr/bin/python3.7m

# round-robin-stimuli-gen.py

import brian2 as b
import matplotlib.pyplot as plt
from numpy import save
print("\nLibraries loaded.")

b.start_scope()

time_per_neuron = 400*b.ms
n_times = 100
n_neurons = 2
freq = 50*b.Hz

P = b.PoissonGroup(1, freq)
M = b.SpikeMonitor(P)
b.store()

print("Simulating...", end='', flush=True)
spike_times = []
spike_indices = []
start_time = 0
for k in range(n_times):
    for n in range(n_neurons):
        b.restore()
        b.run(time_per_neuron)
        percentage = 100.0*(k*n_neurons + n)/(n_times*n_neurons + 0.0)
        print("\rSimulating... t={}%".format(round(percentage, 2)), end='', flush=True)
        spike_times += [a + start_time for a in list(M.t)]
        spike_indices += [n]*M.num_spikes
        start_time += time_per_neuron
print("\rSimulating... done")

# Save the arrays
filename = '{}-round-robin-stimulus.npy'.format(n_neurons)
print("Saving arrays to '{}'... ".format(filename), end='', flush=True)
save(filename, [spike_times, spike_indices])
print("done")

a = input("Show raster-plot? (y/n): ")
if a == 'y':
    plt.figure('float')
    plt.plot(spike_times, spike_indices, '.k')
    plt.show()
