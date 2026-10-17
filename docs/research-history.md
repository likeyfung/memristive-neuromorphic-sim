# Development history

The project has several branches. Some revisions introduce a model, others change a task or audit an earlier result. Version numbers track that work; they are not a sequence of interchangeable benchmark releases. The [archive index](history/INDEX.json) contains the available original notes.

## Memristive model and early wave simulations

The code at the repository root is the original memristive model. It explores retention timescales, recurrent modules, population coding, and spiking gating on delayed matching and temporal-order tasks. The later Wave Cognition work uses a separate implementation.

V1–V5 developed behavioral neuron/wave demonstrations and scale checks, including 4,096-node tests. These used engineered tasks and replicated structures. V6 separated the application model, task engine, and circuit checks. V7 explored phase-addressed memory with trained reciprocal couplers; V8 replaced ideal write/read interfaces with explicit synaptic, dendritic, and somatic dynamics and spike-count output.

## Loading, feedback, and fair comparisons: V9–V21

V9 audited the earlier results. V10–V13 examined loading, corrected the global-coupling topology, compared state aggregation, and introduced mismatch, trim, and time-scaling studies. V12 did not establish a matched ASIC advantage. This made it necessary to distinguish numerical simplification from physical latency or energy savings.

V14 consolidated the shared-state array. V15 added heterogeneous feedback and causal interventions. V16–V18 used streaming tasks and digital controls; V18 reused V17's data, so it was not an independent test cohort. V19 introduced a modular recurrent reservoir with 256 neurons and 16 shared tiles.

V20 formalized equal-budget calibration followed by a source/parameter freeze and new test histories. It calibrated operating points and readouts rather than learning recurrent synapses. V21 then examined conductance learning and the contribution of continuous state.

## Neuronal selection and unsuccessful adaptation: V22–V30

V22 changed the behavioral interface: the answer had to come from neuronal ensembles, without a task decoder reading internal wave amplitude or phase. V23 separated controlled-state selection from behavior driven by natural input histories. V24 trained the upstream writer while keeping the selector fixed.

V25 compared plasticity at input and recurrent synapses. V26 used a supervised reachability test to separate representational limits from failure of a local learning rule. V27 found redundant directions in the input conductance mapping: separately stored weights did not always provide independent control over inputs.

V28 tested separated afferents, but both selected networks still scored 50% on 64 fresh reversal trials and chose the same ensemble. Better internal margins did not translate into correct switching. V29 introduced staged checks, while V30 kept memory, adaptation, and attention experiments in separate checkpoints. Their results describe different trained configurations.

## Learned memory and the recovered V40 lineage

Later V32–V39 work developed learned neuronal memory, adaptation, and endogenous modulation. The recovered V40 archive became the main continuation point. Audited V32/V37 records and intermediate dependencies are present in that lineage, though complete standalone packages for every revision are not available here.

V40's primary cohort reached mean F1 0.965 with 85 of 96 exact completions. Its adaptation-off comparison did not demonstrate a benefit from adaptation, and disabling reader sources still succeeded in the reported causal cohort. These controls narrowed the interpretation of which parts of the model were doing useful work. See the [lineage audit](history/notes/research__model_lineage_audit__FINDINGS.txt).

## Connectivity and navigation branch: V42–V49

The V42 navigation work and V43–V44 audits used application-specific, rate-based models. V45 introduced real anatomical connectivity with simplified spiking blocks, but the navigation and timing tests failed. The graph was anatomical; physiological parameters and the motor mapping were engineering assumptions.

V47 checked sparse and dense event delivery on a fixed connectome mapping. V48 moved to a generic programmable neuron/shared-state fabric, and V49 calibrated excitatory and inhibitory input budgets for a FlyWire workload. Those tests concerned firing, dropout, and recovery on synthetic inputs. They did not establish learned navigation or replace the V40 memory model.

## Causal memory and electrical studies: V50–V58

V50 returned to the V40 lineage and tested optional local recurrent regulation. V51 examined the division between stored content and access using six independently acquired memory sets, paired interventions, and a task-aware digital reference.

V52 configured the full neuronal kernel for perturbation replay on an aggregate fly-related workload, with association learning disabled. V53 reviewed the accumulated findings. V54 mapped the V52 workload to behavioral electrical blocks: 256 main cells, 80 inhibitory cells, 16 local states, and 5,112 recurrent contacts.

V55 estimated state, traffic, and power costs. V56 audited the saved electrical traces, separating signal energy from supply energy and the full-array inventory from an equivalent reduced replay. V57 assembled the tapeout cost and calibration questions. These were analyses of existing evidence, not new demonstrations of learning.

V58 returned to the learned-memory configuration. It tested matched present inputs after different histories, equally calibrated local-state controls, and modeled electrical stress. Nominal recall tied the broadcast control, while the spatial model used fewer spikes and tolerated the specified combined stress better. The [experiment report](results-v58.md) gives the design and uncertainty.

## Availability

The public material consists of the original memristive code, this history, aggregate results, and historical reading notes. The newer source and detailed data remain local. Gaps in the numbering, including V31, V41, and V46, should not be read as verified standalone releases. [Archive notes](publication-scope.md) describe the preserved material and checks.
