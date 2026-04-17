# Part 3 & 4: Contraction and Expansion
# AGM belief revision 
# Expansion:   B + phi  =  B ∪ {phi}
# Contraction: B ÷ phi  =  ∩ γ(B ⊥ phi)    [partial meet contraction]
# Revision:    B * phi  =  (B ÷ ¬phi) + phi  [Levi identity]

from itertools import combinations
from copy import deepcopy

from belief_base import BeliefBase, Belief, Atom, Negation
from logicalEntailment import entails


def _make_bb(pairs):
    bb = BeliefBase()
    for belief, priority in pairs:
        bb.beliefs.append((belief, priority))
    bb.beliefs.sort(key=lambda x: x[1])
    return bb


def _temp_bb(beliefs_list):
    return _make_bb([(b, 1) for b in beliefs_list])


def _collect_atoms(bb):
    atoms = set()

    def walk(f):
        if isinstance(f, Atom):
            atoms.add(f)
        elif hasattr(f, 'formula'):       # Negation
            walk(f.formula)
        elif hasattr(f, 'left'):          # Conjunction, Disjunction, Implication, Equivalence
            walk(f.left)
            walk(f.right)

    for belief in bb.get_beliefs():
        walk(belief)

    return atoms


# Expansion — Part 4

def expand(bb: BeliefBase, phi: Belief, priority: int = 1) -> BeliefBase:
    # B + phi = B ∪ {phi}
    new_bb = deepcopy(bb)

    if not new_bb.contains(phi):
        new_bb.add(phi, priority)

    return new_bb


# Contraction — Part 3

def remainder_set(bb: BeliefBase, phi: Belief) -> list:
    # B' ∈ B ⊥ phi  iff  B' ⊆ B  and  B' ⊬ phi  and for every B'' with B' ⊂ B'' ⊆ B : B'' ⊢ phi   (maximality)

    pairs = list(bb.beliefs)
    remainders = []

    for size in range(len(pairs), -1, -1):
        for subset in combinations(pairs, size):

            beliefs_only = [b for b, _ in subset]

            if entails(_temp_bb(beliefs_only), phi):
                continue

            subset_set = set(beliefs_only)
            dominated = any(subset_set < set(r.get_beliefs()) for r in remainders)

            if not dominated:
                remainders.append(_make_bb(list(subset)))

    return remainders


def selection_function(remainders: list) -> list:
    # Different choices of γ give different contraction behaviours:
    #   Full meet:    γ selects all remainders      (most conservative)
    #   Maxichoice:   γ selects exactly one          (most liberal)
    #   Partial meet: γ selects a subset             (what we implement)

    if not remainders:
        return []

    def weight(r):
        return sum(p for _, p in r.beliefs)

    best_weight = max(weight(r) for r in remainders)
    return [r for r in remainders if weight(r) == best_weight]


def contract(bb: BeliefBase, phi: Belief) -> BeliefBase:
    # Partial meet contraction: B ÷ phi = ∩ γ(B ⊥ phi)

    if not entails(bb, phi):
        return deepcopy(bb)  # vacuity postulate

    remainders = remainder_set(bb, phi)
    selected = selection_function(remainders)

    if not selected:
        return deepcopy(bb)  # phi is a tautology — cannot be contracted

    # intersect all selected remainders
    common = set(selected[0].get_beliefs())
    for r in selected[1:]:
        common = common & set(r.get_beliefs())

    priorities = bb.get_priorities()
    result_pairs = [(b, priorities[b]) for b in common]

    return _make_bb(result_pairs)


# Revision — Levi Identity
def revise(bb: BeliefBase, phi: Belief, priority: int = 1) -> BeliefBase:
    # B * phi = (B ÷ ¬phi) + phi   [Levi identity]
    contracted = contract(bb, Negation(phi))
    return expand(contracted, phi, priority)


# AGM Postulate Checks — Success, Inclusion, Vacuity, Consistency, Extensionality
def check_success(bb: BeliefBase, phi: Belief) -> bool:
    # Success: phi ∉ Cn(B ÷ phi)
    contracted = contract(bb, phi)
    return not entails(contracted, phi)


def check_inclusion(bb: BeliefBase, phi: Belief) -> bool:
    # Inclusion: B ÷ phi ⊆ B
    contracted = contract(bb, phi)
    return set(contracted.get_beliefs()).issubset(set(bb.get_beliefs()))


def check_vacuity(bb: BeliefBase, phi: Belief) -> bool:
    # Vacuity: if phi ∉ Cn(B) then B ÷ phi = B
    if entails(bb, phi):
        return True
    contracted = contract(bb, phi)
    return set(contracted.get_beliefs()) == set(bb.get_beliefs())


def check_consistency(bb: BeliefBase, phi: Belief) -> bool:
    # Consistency: B ÷ phi should not derive both an atom and its negation.
    # Bot() not used directly — logicalEntailment can't handle it in clause extraction.
    contracted = contract(bb, phi)
    for atom in _collect_atoms(contracted):
        if entails(contracted, atom) and entails(contracted, Negation(atom)):
            return False
    return True


def check_extensionality(bb: BeliefBase, phi: Belief, psi: Belief) -> bool:
    # Extensionality: if phi ≡ psi then B ÷ phi = B ÷ psi
    c1 = contract(bb, phi)
    c2 = contract(bb, psi)
    return set(c1.get_beliefs()) == set(c2.get_beliefs())

# Demo
if __name__ == "__main__":
    print("=" * 60)
    print("  BELIEF REVISION ENGINE — Part 3 & 4 (Group 45)")
    print("=" * 60)

    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    s = Atom("s")

    bb = BeliefBase()
    bb.add(r, priority=1)       # low entrenchment
    bb.add(p, priority=2)       # medium entrenchment
    bb.add(q, priority=3)       # high entrenchment
    bb.add(p >> q, priority=3)  # background knowledge — high entrenchment

    print("\nInitial belief base:")
    print(bb)
    print(f"  Total beliefs:     {bb.size()}")
    print(f"  Highest priority:  {bb.get_highest_priority_beliefs()}")
    print(f"  Lowest priority:   {bb.get_lowest_priority_beliefs()}")

    print("\n--- Entailment checks (resolution-based) ---")
    print(f"  B ⊢ q?       {entails(bb, q)}")       # True
    print(f"  B ⊢ p >> q?  {entails(bb, p >> q)}")  # True
    print(f"  B ⊢ s?       {entails(bb, s)}")        # False

    print("\n--- Expansion: B + (p & q) ---")
    bb_expanded = expand(bb, p & q, priority=2)
    print(bb_expanded)

    print("--- Expansion: B + p  (p already in B) ---")
    bb_same = expand(bb, p)
    print(bb_same)

    print("\n--- Contraction: B ÷ p ---")
    bb_contracted = contract(bb, p)
    print(bb_contracted)

    print("--- Contraction: B ÷ s  (vacuous — s ∉ Cn(B)) ---")
    bb_vacuous = contract(bb, s)
    print(bb_vacuous)

    print("\n--- Revision: B * ¬p  (Levi identity) ---")
    bb_revised = revise(bb, Negation(p), priority=2)
    print(bb_revised)

    # p vs ~~p are logically equivalent — good test for extensionality
    double_neg_p = Negation(Negation(p))

    print("\n--- AGM Postulate Checks on B ÷ p ---")
    print(f"  Success:                    {check_success(bb, p)}")
    print(f"  Inclusion:                  {check_inclusion(bb, p)}")
    print(f"  Vacuity (÷ s):              {check_vacuity(bb, s)}")
    print(f"  Consistency:                {check_consistency(bb, p)}")
    print(f"  Extensionality (p vs ~~p):  {check_extensionality(bb, p, double_neg_p)}")

    print("\nAll checks should be True.")
