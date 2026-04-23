# Belief Revision Group 45

This project implements propositional logic belief revision engine in python with the AGM framework and applies it to a Mastermind code-breaker.

## Project Scope

The codebase has two connected parts:

1. A logic and AGM belief revision engine.
2. A Mastermind solver that updates beliefs from black/white feedback and narrows possible codes over time.

## Core Features

- Propositional formula classes with operator overloading.
- Priority-aware belief base.
- Resolution-based entailment via CNF transformation and clause extraction.
- AGM operations:
	- Expansion: B + phi
	- Contraction (partial meet): B / phi
	- Revision (Levi identity): B * phi = (B / ~phi) + phi
- Postulate checks: Success, Inclusion, Vacuity, Consistency, Extensionality.
- Mastermind integration:
	- Generates all candidate codes (6^4 = 1296)
	- Filters by exact feedback simulation each round
	- Applies AGM-safe updates to keep beliefs consistent

## Repository Files

- [belief_base.py](belief_base.py): propositional logic data structures and belief base implementation.
- [logicalEntailment.py](logicalEntailment.py): CNF conversion, clause extraction, resolution, and entailment.
- [belief_revision_agent.py](belief_revision_agent.py): contraction, expansion, revision, and AGM postulate checks.
- [mastermind.py](mastermind.py): Mastermind solver using candidate filtering plus AGM belief updates.
- [requirements.txt](requirements.txt): Python dependency list.

## Installation

```bash
pip install -r requirements.txt
```

## How To Run

Run logic entailment demo:

```bash
python logicalEntailment.py
```

Run belief base demo:

```bash
python belief_base.py
```

Run contraction, expansion, and AGM revision demo:

```bash
python belief_revision_agent.py
```

Run Mastermind demo + performance test:

```bash
python mastermind.py
```

## Mastermind Workflow

At each guess:

1. Compute feedback (black, white).
2. Convert that feedback into logical constraints.
3. Update the belief base using expansion or revision depending on contradiction.
4. Filter candidate codes to those that would return the same feedback.
5. Pick the next candidate that is belief-consistent.

This combines direct simulation pruning with symbolic consistency checks.

## Minimal Example

```python
from belief_base import Atom, BeliefBase
from logicalEntailment import entails

p = Atom("p")
q = Atom("q")

bb = BeliefBase()
bb.add(p >> q)
bb.add(p)

print(entails(bb, q))  # True
```

## Notes

- Optional CNF validation helpers in [logicalEntailment.py](logicalEntailment.py) use SymPy.
- The current Mastermind script includes three demo runs and a 500-game performance sweep.



