# Belief Revision Group 45
# TODO: finish readme

This project implements a small propositional logic belief base and a resolution-based entailment checker in Python.

## What It Does

- Stores propositional beliefs with optional priorities.
- Lets you build formulas with Python operators.
- Converts formulas to conjunctive normal form (CNF).
- Extracts clauses and performs resolution.
- Checks whether a belief base entails a query.
- Includes optional SymPy-based CNF validation for testing.

## Files

- [belief_base.py](belief_base.py): propositional logic data structures and belief base implementation.
- [logicalEntailment.py](logicalEntailment.py): CNF conversion, clause extraction, resolution, and entailment.
- [requirements.txt](requirements.txt): Python dependency list.

## Installation

Install the required package with:

```bash
pip install -r requirements.txt
```

## Usage

Run the entailment demo:

```bash
python logicalEntailment.py
```

Run the belief base demo:

```bash
python belief_base.py
```

## Example

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

- The optional CNF comparison helpers in [logicalEntailment.py](logicalEntailment.py) use SymPy.
- The project is intended for propositional logic only.



