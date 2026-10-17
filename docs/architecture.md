# Model

The current memory model separates the connections that store an association from the state that makes it accessible. A partial cue activates learned recurrent connections. Earlier activity changes a local continuous state, which acts through dendritic and inhibitory pathways to favor one reader population over another.

## Neural dynamics

| Component | Configuration | Role |
|---|---|---|
| Main neurons | 256 cells, twelve reduced dendritic compartments each | Synaptic integration and recurrent pattern completion |
| Inhibitory neurons | 80 cells across sixteen tiles | PV inhibition and paired SST/VIP gating |
| Shared state | Sixteen nonoscillatory scalar states | Retain history and interact through local coupling |
| Recurrent synapses | Bounded weights acquired through local pre/post activity | Store learned associations |
| Behavioral output | Reader-neuron spikes | Express recalled features without a direct shared-state decoder |

V58 contains 256 main neurons and 80 inhibitory neurons arranged over 16 tiles. Each main neuron has twelve reduced dendritic compartments: eight basal, three apical, and one trunk. Inputs pass through AMPA/NMDA-like filters before dendritic integration and a threshold/reset soma. The inhibitory population contains PV and paired SST/VIP motifs.

Writer spikes drive the local continuous state. Neighboring tiles exchange state through reciprocal coupling, and local detectors feed back into the inhibitory circuit. Reader neurons then respond to a partial sensory cue and learned recurrent input. Their spikes are the behavioral output; the evaluator has no direct access to the shared-state coordinates.

The selected V58 configuration uses sixteen nonoscillatory scalar states. Reader emission is disabled, so the demonstrated modulation path runs from writers, through shared state, to readers. A benefit from reciprocal reader emission has not been established.

These are reduced engineering models of neurons and synapses. Their compartment names and inhibitory labels describe the intended mechanisms, but the model has not been fitted to a particular recorded biological circuit.

## Learning and recall

Association acquisition uses bounded local pre/post potentiation. Learned recurrent feedback is disabled during acquisition and enabled for recall. Operating points are calibrated on training histories and selected on separate validation histories. For V58, six final memory sets are acquired and their weights frozen before new test histories are generated.

Inference consists of integrating synaptic, dendritic, inhibitory, and continuous-state dynamics. There is no fitted classifier on the shared state in the behavioral path. Pattern completion is assessed by whether uncued feature neurons become active in the appropriate population.

V58 therefore tests learned associations under frozen recall. Earlier attempts at online adaptation use different protocols and checkpoints; they are described in the [development history](research-history.md).

## Numerical implementation

The full solver represents all twelve dendritic compartments. A compact solver groups equivalent basal branches when their input maps and parameters satisfy the required symmetry. Full and compact spike outputs are checked against each other. This reduction depends on the configured circuit and cannot be assumed for arbitrary compartment models.

## Circuit interpretation

The proposed physical implementation represents dynamics using local capacitive states, conductance/current paths, comparators, and reset circuitry. A neuron would not execute ALU instructions, but it would retain information in voltages, filter states, adaptation, and synaptic conductances. The Python simulator uses ordinary CPU arithmetic and memory to integrate those equations.

Programming, routing, calibration, and input/output circuitry remain part of the implementation cost. The behavioral electrical models do not yet provide a transistor-level design or a measured supply-energy comparison.

V54 mapped a V52 neural workload to electrical blocks. V58 uses the related learned-memory configuration and tests a smaller electrical loop under disturbances. Those experiments address different configurations; the full memory task has not been validated as a fabricated circuit.

The earlier [root-level memristive implementation](../README.md#running-the-original-model) is a separate code lineage with an external task decoder. Its results should be read separately from the current neuronal-output experiments.
