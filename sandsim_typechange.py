import matplotlib.pyplot as plt
from matplotlib import pyplot as plt, colors
from array import array
import numpy as np
import ROOT
import time, sys, glob

# Change font of labels and ticks
from matplotlib import rc
rc('font',**{'family':'serif','serif':['Times'], 'size':'17'})
rc('text', usetex=True)

# Count events
def event_counter(intVolume):

    # All permutations with two digits from 1 to 6.
    possible_type_changes = [    1, 2, 3, 4, 5, 6, 
                                12, 13, 14, 15, 16, 
                                21, 22, 23, 24, 25, 26,
                                31, 32, 33, 34, 35, 36, 
                                41, 42, 43, 44, 45, 46, 
                                51, 52, 53, 54, 55, 56, 
                                61, 62, 64, 64, 65, 66,
                            ]

    # Count how many times a permutation occurs
    # in intVolumes
    counter = [0]*66
    fpossible = []
    for volume in intVolume:
        for j in possible_type_changes:
            if volume == j:
                counter[j] += 1
                if (str(j) not in fpossible):
                    fpossible.append(str(j))

    # Return only possible permutations with 
    # non-zero counts
    return fpossible, [ count for count in counter if count > 0.]

# Bins
def find_bins(all_momentum, fixed_bin_momentum):
    return np.arange(min(all_momentum),max(all_momentum)+fixed_bin_momentum, fixed_bin_momentum)


# Test arguments
if (len(sys.argv)) != 2:
    print("Usage: python 0.5")
    print("To analyze 50 percent of events in chain.")
    sys.exit(1)

# Percentage
percentage = float(sys.argv[1])
if percentage == 1.:
    print("All events will be analysed. This will take a while...")
else:
    print(f"Only the first {percentage*100.:4.2f}% of events will be used." )

# Choosing fonts
mono_font = {'fontname':'monospace'}
serif_font = {'fontname':'serif'}

# Work dir
work_dir = "/home/koerich/simulation_data/effective_model-fixed_volumes2"

# Find all files with sim*root in said 
sim_files = glob.glob(f"{work_dir}/sim.effective.11m-0.0001-new_materials-*.root")
figure_name = "./figure-typechange-10m-0.0001-new_materials.png"

# Chaining root files
t1 = ROOT.TChain("h1000")
for file in sim_files:
    t1.Add(file)

# list of branches:
# EventId
# EventVtx
# NuFlavor
# IntMaterial
# IntVolume
# NuMomentum[3]
# NStateChange
# Position[4]
# Momentum[3]
# Pid
# Type

# C-like array for storing event's array
interaction_volume_C  = array('i', [0])
nstate_change_C = array('i', [0])

# Get branches
interaction_volume_branch = t1.GetBranch("IntVolume")
nstate_change_brach = t1.GetBranch("NStateChange")
momentum_branch = t1.GetBranch("Momentum")
pid_branch = t1.GetBranch("Pid")

# Take branches to the arrays
t1.SetBranchAddress("IntVolume", interaction_volume_C)
t1.SetBranchAddress("NStateChange", nstate_change_C)

# Number of events to analyse
N1 = t1.GetEntries()
print(N1, " total events in chain 1.")

# N2 = t2.GetEntries()
N1 = int(N1*percentage)
print(N1, " events to be analysed in chain 1.")

# Arrays for each component of vertex
intVolume = array('i',[0]*N1)
NStateChange = []


pid, momentum, change_type = [], [], []
# Retrieve information stored in each event
for i in range(0, N1):
    
    # Print progress
    print("Creating arrays for Type change: {0:03d}%.".format(int(i/N1*100)), end="\r")
    
    # Get value of entry
    t1.GetEntry(i) 

    # Store value in array
    intVolume.append(interaction_volume_C[0]) 
    NStateChange.append(nstate_change_C[0])
    pid.append(array('i', [0]*nstate_change_C[0]))
    momentum.append(array('f', [0, 0, 0]*nstate_change_C[0]))
    change_type.append(array('i', [0]*nstate_change_C[0]))
    # momentum.append( np.empty( (20, 3), float)  )

# Finish progression
print("Creating arrays for Type change: 100%")    

# Start with momentum and id
for i in range(0,N1):
    
    # Print
    print("Filling arrays of Type change: {0:03d}%.".format(int(i/N1*100)), end="\r")

    # Set address
    t1.SetBranchAddress("Type", change_type[i])
    
    # Get event
    t1.GetEntry(i)

# Print
print("Filling arrays of Type change: 100%.")

# Find all type changes
all_change_types = np.concatenate( (change_type), axis=None)

# Counting 
print("Counting events of each type...")
possible_types, type_counts = event_counter(all_change_types)

# Type counts that are not zero
print("Finding of types that happened.")
type_bins = []
for i in range(0, len(type_counts)):
    
    if (i not in type_bins) and (type_counts[i] > 0):
        type_bins.append(str(i))

# Let user know
print("Saving histogram...")

# Plot stuff
fig2, ax21 = plt.subplots(nrows=1, ncols=1, figsize=(6,6)) 

# Bar histogram
print(possible_types, type_counts)
bar = ax21.bar(possible_types, type_counts, hatch=r'\\\\', edgecolor='black', facecolor='white', linewidth=1.5)

# Add labels
ax21.set_ylabel("No. of events")
ax21.set_xlabel("Type of volume change")

# Add title
fig2.suptitle(f"{len(all_change_types)} events")

# Tight layout
plt.tight_layout()

# Save image
plt.savefig(figure_name)