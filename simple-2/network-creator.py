#! /usr/bin/python3.7m

import brian2 as b
import numpy as np
import matplotlib.pyplot as plt

b.start_scope()

# ----------
# PARAMETERS
# ----------
t_simul = 40*b.second
n_neurons = 2
n_inputs = 3

# basic neuron functioning
tau_mem = 100*b.ms
t_refractory = 20*b.ms
v_rest = 0
v_max = 26

# homeostasis
tau_homeostasis = 10*b.second
v_thresh_0 = -7
v_thresh_init = 13  # taken by Diehl and Cook, relative to V_rest
del_v_thresh = 1.2
v_thresh_max = 40

# lateral inhibition
t_inhibit = t_refractory

# stdp
tau_Apre = 40*b.ms
tau_Apost = 400*b.ms
Apre_reset = 1.8
Apost_reset = 0.25
w_min = 0.5
w_max = 20

eta = 1

# filenames
stimuli_filename = "/home/ven0m/code/btp/simple-2/stimulus.npy"

# ----------------------------
# Creating the neuron (output)
# ----------------------------
print("Creating neurons... ", end='', flush=True)
eqns = '''
not_inhibited : boolean
inhibiting : boolean
dv_thresh/dt = -(v_thresh - v_thresh_0)/tau_homeostasis : 1
dv/dt = -(v - v_rest)*int(not_inhibited)/tau_mem : 1 (unless refractory)
'''
reset = '''
v = v_rest
v_thresh = (v_thresh + del_v_thresh)*int(v_thresh < v_thresh_max - del_v_thresh) + v_thresh_max*int(v_thresh >= v_thresh_max - del_v_thresh)
'''

G_op = b.NeuronGroup(n_neurons, eqns, method='exact',
                  refractory=t_refractory,
                  threshold='v>v_thresh',
                  reset=reset,
                  events={'stop_inhibition':'(t > lastspike + t_inhibit) and inhibiting'}
                  )
G_op.not_inhibited = True
G_op.inhibiting = False
G_op.v_thresh = v_thresh_init
G_op.v = [2]

M1= b.SpikeMonitor(G_op)
SM_neuron = b.StateMonitor(G_op, ['v', 'v_thresh', 'not_inhibited', 'inhibiting', 'not_refractory'], record=True)
print("done")

# ----------------------------
# Creating Inhibitory Synapses
# ----------------------------
print("Creating inhibitory synapses... ", end='', flush=True)
S_inhibit = b.Synapses(G_op, G_op,
                      on_pre={'pre':'''
                                 v_post = 0
                                 not_inhibited_post = False
                                 inhibiting_pre = True
                                 ''',
                             'inh_done':'''
                                 not_inhibited_post = True
                                 inhibiting_pre = False
                                '''},
                      on_event={'pre':'spike',
                               'inh_done':'stop_inhibition'})
S_inhibit.connect(condition='i!=j', p=1)
print("done")

# -------------
# Input Stimuli
# -------------
print("Loading input stimuli... ", end='', flush=True)
stimuli = np.load(stimuli_filename)
times = [a*b.second for a in stimuli[0]]
G_in = b.SpikeGeneratorGroup(n_inputs, indices=stimuli[1], times=times)
print("done")


# -----------------------
# Creating input Synapses
# ------------------------
print("Preparing input synapse... ", end='', flush=True)
model = '''
w : 1
dApre/dt = -Apre/tau_Apre : 1 (event-driven)
dApost/dt = -Apost/tau_Apost : 1 (event-driven)
'''
stdp_pre = '''
v_post = (v_post + eta*w*int(not_inhibited))*int(v_post <= v_max - w) + v_max*int(v_post > v_max-w);
Apre = Apre_reset;
w = (w - Apost)*int(w > w_min + Apost) + w_min*int(w <= w_min + Apost)'''
stdp_post = 'Apost = Apost_reset; w = (w+Apre)*int(w < w_max - Apre) + w_max*int(w >= w_max - Apre)'

S_in = b.Synapses(G_in, G_op, method='exact',
                  model=model, 
                  on_pre=stdp_pre,
                  on_post=stdp_post)
S_in.connect()
S_in.w[:] = "3 + rand()"
S_in.Apre = 0
S_in.Apost = 0

SM_synapse = b.StateMonitor(S_in, 'w', record=True)
print("done")

# -------------
# Store network
# -------------
'''
net = b.Network(G_op, G_in, M1, SM_neuron, SM_synapse, S_inhibit, S_in)
print("Network prepared")
print("Storing... ", end='', flush=True)
net.store(filename=network_filename)
print("done")
'''

# ----------
# Simulation
# ----------
def reporter(elapsed, complete, start, duration):
    print("\rSimulating... {}%".format(round(complete*100, 2)), end='', flush=True)
    
# run simulation
print("Simulating... ", end='', flush=True)
b.run(t_simul, report=reporter, report_period=t_simul/100)
print('\rSimulating... done')

# ----
# Plot
# ----
print("Plotting...", end='', flush="True")
clist = ['orange', 'g', 'r']
plt.figure("float{}".format(k))
for k in range(n_neurons):
    plt.subplot(n_neurons + 1, 1, k+1)
    plt.plot(SM_neuron.t/b.second, SM_neuron.v[k], color='b', label='{}_v_mem'.format(k))
    plt.plot(SM_neuron.t/b.second, SM_neuron.v_thresh[k], color='b', linestyle='--', label='{}_v_thresh'.format(k))
    plt.plot(SM_neuron.t/b.second, SM_neuron.inhibiting[k]*1, color='black', linestyle=':', label='{}_inh'.format(k))
    for l in range(n_inputs):
        plt.plot(SM_synapse.t/b.second, SM_synapse[S_in[l, k]].w[0] , color=clist[l], label='{}_{}_w'.format(l, k))
    plt.legend()
    for l in range(len(M1.t)):
        if M1.i[l] == k:
            plt.axvline(M1.t[l]/b.second, linestyle=':', color='b')

# plotting input
# first, restrict to area till my time
time_cap = 0
for i in range(len(times)):
    if times[i] > t_simul :
        time_cap = i
        break
plt.subplot(n_neurons + 1, 1, n_neurons +1)
plt.plot(times[:time_cap]/b.second, stimuli[1][:time_cap], '.k')
print("done")
plt.show()
