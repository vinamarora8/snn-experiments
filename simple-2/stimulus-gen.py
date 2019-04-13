#! /usr/bin/python3.7m

# round-robin-stimuli-gen.py

import brian2 as b
import matplotlib.pyplot as plt
import numpy as np
print("\nLibraries loaded.")

b.start_scope()

time_per_neuron = 400*b.ms
n_times = 100
n_neurons = 2
freq = 50*b.Hz

P = b.PoissonGroup(1, freq)
M = b.SpikeMonitor(P)
b.store()

print("Simulating-1...", end='', flush=True)
spike_times = []
spike_indices = []
start_time = 0
for k in range(n_times):
    for n in range(n_neurons):
        b.restore()
        b.run(time_per_neuron)
        percentage = 100.0*(k*n_neurons + n)/(n_times*n_neurons + 0.0)
        print("\rSimulating-1... t={}%".format(round(percentage, 2)), end='', flush=True)
        spike_times += [a + start_time for a in list(M.t)]
        spike_indices += [n]*M.num_spikes
        start_time += time_per_neuron
print("\rSimulating-1... done")

print("Simulating-2... ", end='', flush=True)
b.restore()
b.run(time_per_neuron*n_neurons*n_times)
spike_times += list(M.t)
spike_indices += [n_neurons]*M.num_spikes
print("done")


# Rearrange times and indices
spike_times /= b.second
index_array = np.argsort(spike_times)
spike_times = spike_times[index_array]
spike_indices = np.array(spike_indices)
spike_indices = spike_indices[index_array]


# Save the arrays
filename = '/home/ven0m/code/btp/simple-2/stimulus.npy'
print("Saving arrays to '{}'... ".format(filename), end='', flush=True)
np.save(filename, [spike_times, spike_indices])
print("done")

a = input("Show raster-plot? (y/n): ")
if a == 'y':
    plt.figure('float')
    plt.plot(spike_times, spike_indices, '.k')
    plt.show()
