# Belief Revision Group 45

This project implements a propositional logic belief revision engine in Python, based on the AGM model (Alchourron, Gardenfors, Makinson, 1985).

## What It Does

- Stores propositional beliefs with optional priorities.
- Lets you build formulas with Python operators.
- Converts formulas to conjunctive normal form (CNF).
- Extracts clauses and performs resolution.
- Checks whether a belief base entails a query.
- Includes optional SymPy-based CNF validation for testing.
- Contracts beliefs from the base using partial meet contraction.
- Expands the belief base with new beliefs.
- Revises the belief base using the Levi identity.
- Verifies AGM postulates: Success, Inclusion, Vacuity, Consistency, Extensionality.

## Files

- [belief_base.py](belief_base.py): propositional logic data structures and belief base implementation.
- [logicalEntailment.py](logicalEntailment.py): CNF conversion, clause extraction, resolution, and entailment.
- [belief_revision_agent.py](belief_revision_agent.py): contraction, expansion, revision, and AGM postulate checks.
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

Run the contraction, expansion and revision demo:

```bash
python belief_revision_agent.py
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
- Revision is implemented via the Levi identity: B * φ = (B ÷ ¬φ) + φ.



