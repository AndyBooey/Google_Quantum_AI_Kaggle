Google Quantum AI – Verifiable Quantum Circuit Compilation
Two-person Kaggle project plan for the Google Quantum AI – Verifiable Quantum Circuit Compilation competition.

The goal of this project is to improve the provided quantum circuit compilations so they use fewer expensive resources while remaining correct under the competition verifier.
1. Project Goal
We are optimizing three competition benchmarks:
1. invsqrt – Fusion Energy
   Optimize a reversible fixed-point inverse-square-root circuit used for 1/sqrt(x) phasing.
2. dqi – Combinatorial Optimization
   Optimize a reversible Reed–Solomon syndrome decoder used in Decoded Quantum Interferometry.
3. dfthcsos – Quantum Chemistry / Clean Energy
   Optimize the factorization, Givens tree, angle precision, and QROM-based angle-loading circuits used in Hamiltonian block encoding.
The general objective is:
Start with a valid baseline
        ↓
Measure its cost
        ↓
Change one thing
        ↓
Run the verifier
        ↓
If incorrect → reject
If correct → compare cost
        ↓
Keep only measurable improvements
        ↓
Repeat
2. Team Roles
We will split the work so that both teammates can work in parallel without constantly editing the same code.
Teammate A – Circuit / Algorithm Optimization
Primary responsibility:
- Understand the baseline circuit implementations
- Study reversible computation patterns
- Reduce Toffoli count
- Reduce ancilla / logical qubit usage
- Experiment with arithmetic simplifications
- Work primarily on invsqrt
- Later investigate circuit-level improvements for dqi
- Review dfthcsos QROM / ANGLE circuits
Main questions:
Can this operation be removed?
Can two operations be combined?
Can an intermediate value be reused?
Can an ancilla be avoided?
Can something be uncomputed more cheaply?
Can lower precision still pass?
Expected outputs:
- optimized .kmb / .kmx circuits
- scripts that generate those circuits
- notes explaining each optimization
- before/after Toffoli and qubit counts
Teammate B – Verification / Search / Benchmark Infrastructure
Primary responsibility:
- Get the official baseline running
- Understand the verifier and scoring
- Build experiment automation
- Record results
- Test candidate circuits
- Work primarily on dqi experimentation and failure-rate tradeoffs
- Investigate classical optimization for dfthcsos
- Build scripts for parameter sweeps and automated search
Main questions:
Does this candidate still pass?
How much did its cost improve?
What parameter produced the improvement?
Can we automatically test 10/100/1000 variations?
What is the best tradeoff between correctness and cost?
Expected outputs:
- verification scripts
- benchmark scripts
- experiment tables
- automated parameter searches
- submission packaging scripts
- leaderboard tracking notes
3. Shared Responsibilities
Both teammates should understand enough of the full project to review each other's work.

Both teammates should:
- learn basic quantum-circuit vocabulary
- understand Toffoli gates
- understand ancillas
- understand reversible computation
- understand uncomputation
- understand what the verifier checks
- review important pull requests
- reproduce major improvements
- document every leaderboard submission
No optimization should be accepted only because:
"It seems faster."

It should have measurements.
4. Suggested Repository Structure
google-quantum-kaggle/
│
├── README.md
│
├── requirements.txt
│
├── .gitignore
│
├── docs/
│   ├── quantum_notes.md
│   ├── competition_notes.md
│   ├── invsqrt_notes.md
│   ├── dqi_notes.md
│   └── dfthcsos_notes.md
│
├── baseline/
│   ├── invsqrt/
│   ├── dqi/
│   └── dfthcsos/
│
├── src/
│   ├── invsqrt/
│   ├── dqi/
│   ├── dfthcsos/
│   └── common/
│
├── experiments/
│   ├── invsqrt/
│   ├── dqi/
│   └── dfthcsos/
│
├── scripts/
│   ├── verify.py
│   ├── benchmark.py
│   ├── build_submission.py
│   └── run_experiment.py
│
├── results/
│   ├── experiment_log.csv
│   └── leaderboard_log.csv
│
└── submissions/
5. Git Workflow
Use separate branches.

Example:
main
dev
feature/invsqrt-newton
feature/invsqrt-precision
feature/dqi-decoder
feature/dqi-search
feature/dfthcsos-qrom
feature/experiment-runner
Recommended workflow:
git checkout dev
git pull

git checkout -b feature/my-experiment
Do not develop directly on main.

Use:
- main = known-good submission code
- dev = integrated experimental code
- feature branches = individual experiments
6. Pull Request Rule
Every meaningful optimization should include:
What changed:
Why it might help:
Verifier result:
Old Toffoli count:
New Toffoli count:
Old qubit count:
New qubit count:
Accuracy / failure result:
Files changed:
How to reproduce:
Example:
Optimization:
Reduced fixed-point precision from 32 to 29 fractional bits.

Reason:
The benchmark tolerance may not require the extra three bits.

Verifier:
PASS

Before:
Toffoli = 48,200
Qubits = 164

After:
Toffoli = 44,750
Qubits = 158

Difference:
-3,450 Toffoli
-6 qubits

Reproduce:
python scripts/run_experiment.py --task invsqrt --config configs/invsqrt_29bit.yaml
7. Phase 1 – Get the Baseline Running
Do this before attempting major optimizations.
Teammate A
- [ ] Read the invsqrt baseline
- [ ] Identify inputs and outputs
- [ ] Identify expensive arithmetic operations
- [ ] Locate Toffoli-heavy sections
- [ ] Identify ancillas
- [ ] Draw a simplified flow of the algorithm
Example:
input x
  ↓
initial approximation
  ↓
refinement
  ↓
fixed-point operations
  ↓
phase result
  ↓
uncompute temporary values
Teammate B
- [ ] Install competition dependencies
- [ ] Run official examples
- [ ] Run verifier
- [ ] Record original baseline costs
- [ ] Understand submission file generation
- [ ] Build one command that evaluates a candidate
Target command:
python scripts/benchmark.py --task invsqrt
Desired output:
Task: invsqrt
Verification: PASS
Toffoli count: XXXXX
Logical qubits: XXX
Score / cost: XXXXX
8. Phase 2 – Learn Only the Quantum Concepts We Need
Do not try to learn all of quantum mechanics.

Focus on:
Required
- bit vs qubit
- quantum circuit
- NOT gate
- controlled-NOT
- Toffoli gate
- reversible computing
- ancilla
- uncomputation
- measurement-based uncomputation
- fixed-point arithmetic
- kickmix circuits
Learn later
- quantum interference
- phases
- QROM
- Reed–Solomon codes
- finite fields
- Givens rotations
- Hamiltonians
- block encoding
Probably unnecessary at first
- Schrödinger equation derivations
- quantum field theory
- full quantum mechanics proofs
- hardware physics
9. Phase 3 – Focus on invsqrt First
Both teammates should begin here because it is the easiest benchmark to understand.

The target computation is related to:
1 / sqrt(x)
Possible optimization directions:
Precision
Try reducing:
number of integer bits
number of fractional bits
intermediate precision
rounding precision
Test the smallest precision that still passes.
Initial Approximation
Investigate whether the starting estimate can be improved.

A better initial approximation may allow:
fewer refinement steps
which may save many gates.
Newton / Refinement Steps
If the baseline uses iterative refinement:
guess
 ↓
Newton step
 ↓
Newton step
 ↓
result
test whether:
guess
 ↓
better Newton step
 ↓
result
can meet the required error tolerance.
Arithmetic Simplification
Look for expensive:
multiplication
division
comparison
lookup
copy
temporary register
operations.

Ask whether they can be replaced with:
shift
constant multiplication
lookup
approximation
reuse
Ancilla Reduction
Find temporary values.

Example:
temp1 = ...
temp2 = ...
temp3 = ...
Determine whether registers can be reused after their values are no longer needed.
10. Phase 4 – dqi
After both teammates understand the workflow, move one person primarily onto dqi.

Important idea:

The decoder may be allowed to fail occasionally.

Therefore the optimization target is not necessarily:
perfect decoder
but potentially:
slightly imperfect decoder
+
much cheaper circuit
Potential experiments:
- reduce decoder precision
- simplify rare branches
- special-case common inputs
- compare alternate Reed–Solomon algorithms
- reduce workspace
- measurement-based cleanup
- approximate decoding
- automated circuit search
Teammate B should maintain:
cost vs failure rate
results.

Example:
Version	Toffoli	Qubits	Failure Rate	Accepted
baseline	1,000,000	500	0.00%	Yes
exp-01	850,000	480	0.01%	Yes
exp-02	650,000	420	0.30%	Maybe
exp-03	400,000	350	10.0%	No


11. Phase 5 – dfthcsos
Treat this task as two connected problems.
Classical side
Optimize:
- tensor factorization
- approximation accuracy
- number of factors
- Givens tree structure
- bit precision
Quantum side
Optimize:
- QROM lookup cost
- ANGLE circuits
- ancilla usage
- Toffoli count
- circuit width
Suggested split:
Teammate A
ANGLE circuits
QROM
circuit construction
ancilla reduction
Teammate B
factorization
Givens tree
precision sweep
classical optimization
Then combine the best compatible results.
12. Experiment Template
Every experiment should have an ID.

Example:
INV-001
INV-002
DQI-001
DFT-001
Use this template:
# Experiment: INV-001

## Hypothesis

Reducing fractional precision from 32 bits to 28 bits will reduce
Toffoli count while remaining within the required accuracy.

## Baseline

Toffoli:
Qubits:
Precision:
Verifier:

## Change

Describe exactly what changed.

## Result

Verifier:
Toffoli:
Qubits:
Accuracy:
Runtime:

## Difference

Toffoli saved:
Qubits saved:
Percentage improvement:

## Conclusion

KEEP / REJECT / INVESTIGATE

## Next Experiment

What should we try next?
13. Experiment Log
Maintain results/experiment_log.csv.

Suggested columns:
experiment_id,date,author,task,description,verified,toffoli,qubits,error,failure_rate,score,status,commit
Example:
INV-001,2026-11-03,A,invsqrt,reduce precision 32->30,yes,45000,154,1e-8,,1.07,keep,abc123
INV-002,2026-11-03,A,invsqrt,reduce precision 30->26,no,39000,148,0.002,,0,reject,def456
This prevents repeating failed ideas.
14. Daily Workflow
Each work session:
1. Pull latest dev
2. Pick ONE hypothesis
3. Create experiment branch
4. Change ONE major variable
5. Run verifier
6. Benchmark
7. Record result
8. Commit
9. Open PR if improvement is real
Avoid changing five things at once.

Otherwise we will not know which change caused the improvement.
15. Weekly Team Meeting
Once per week, review:
Best invsqrt result
Best dqi result
Best dfthcsos result

Biggest Toffoli reduction
Biggest qubit reduction
Failed ideas
Promising unexplored ideas
Leaderboard change
Goals for next week
Keep a section in the README or a separate file:
docs/weekly_notes.md
16. Definition of "Done" for an Optimization
An optimization is not complete until:
- [ ] verifier passes
- [ ] cost measured
- [ ] result recorded
- [ ] code committed
- [ ] experiment can be reproduced
- [ ] teammate can reproduce it
- [ ] submission packaging still works
17. Submission Checklist
Before uploading to Kaggle:
submission.zip
│
├── invsqrt.kmb OR invsqrt.kmx
├── dqi.kmb OR dqi.kmx
└── dfthcsos/
    ├── angle_k_0.kmb OR .kmx
    ├── angle_k_1.kmb OR .kmx
    ├── ...
    └── submission.npz
Check:
- [ ] all required files exist
- [ ] ANGLE numbering starts at 0
- [ ] no gaps in ANGLE numbering
- [ ] submission.npz has required arrays
- [ ] final local verification passes
- [ ] final commit hash recorded
- [ ] zip generated automatically
- [ ] Kaggle score recorded after submission
18. Leaderboard Log
Maintain:
results/leaderboard_log.csv
Suggested columns:
date,submission_name,commit,public_score,invsqrt_notes,dqi_notes,dfthcsos_notes
Never upload:
submission_final_v2_REAL_final_fixed.zip
Use meaningful names:
2026-11-05_inv_precision30_dqi_base.zip
2026-11-08_inv_newton1_dqi_search03.zip
19. Research Template
When reading papers, documentation, or Kaggle discussions:
# Source

Title:
Link:
Author:
Date:

## Problem

What problem does this solve?

## Key Idea

Explain it in simple language.

## Possible Competition Use

invsqrt / dqi / dfthcsos

## Expected Benefit

Toffoli reduction?
Qubit reduction?
Accuracy improvement?

## Difficulty

Easy / Medium / Hard

## Experiment

What exact experiment can we run based on this idea?
Do not collect papers without turning them into experiments.
20. Priority Order
Recommended project order:
1. Environment setup
2. Baseline verification
3. Baseline measurements
4. invsqrt understanding
5. invsqrt simple optimization
6. experiment automation
7. invsqrt advanced optimization
8. dqi baseline
9. dqi search / approximation
10. dfthcsos classical optimization
11. dfthcsos circuit optimization
12. combine improvements
13. repeated leaderboard submissions
21. First Tasks
Teammate A – First Tasks
[ ] Learn Toffoli / ancilla / reversible computing
[ ] Read invsqrt implementation
[ ] Write simplified pseudocode
[ ] Identify three expensive sections
[ ] Find all configurable precision values
[ ] Run first precision experiment
Teammate B – First Tasks
[ ] Install Qualtran / competition tools
[ ] Get baseline running
[ ] Get verifier running
[ ] Record baseline costs
[ ] Create experiment_log.csv
[ ] Build benchmark script
[ ] Build submission-generation script
22. First Joint Milestone
Before attempting advanced ideas, we should be able to do this:
git clone <repo>
pip install -r requirements.txt

python scripts/benchmark.py --task invsqrt
and receive:
Verification: PASS
Toffoli count: ...
Qubit count: ...
Then change one parameter and immediately see whether the circuit became better or worse.

Once this workflow exists, optimization becomes much easier.
23. Main Team Rule
Our project philosophy:
Measure everything. Change one thing at a time. Keep only verified improvements.

A clever-looking idea that cannot pass the verifier is useless.

A tiny verified improvement is progress.

Many tiny improvements can combine into a strong submission.
