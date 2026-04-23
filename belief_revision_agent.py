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


# ==============================================================
# AGM Contraction Postulate Checks
# ==============================================================

def check_contraction_success(bb: BeliefBase, phi: Belief) -> bool:
    # Success: phi ∉ Cn(B ÷ phi)
    contracted = contract(bb, phi)
    return not entails(contracted, phi)


def check_contraction_inclusion(bb: BeliefBase, phi: Belief) -> bool:
    # Inclusion: B ÷ phi ⊆ B
    contracted = contract(bb, phi)
    return set(contracted.get_beliefs()).issubset(set(bb.get_beliefs()))


def check_contraction_vacuity(bb: BeliefBase, phi: Belief) -> bool:
    # Vacuity: if phi ∉ Cn(B) then B ÷ phi = B
    if entails(bb, phi):
        return True   # phi IS entailed — vacuity places no constraint here
    contracted = contract(bb, phi)
    return set(contracted.get_beliefs()) == set(bb.get_beliefs())


def check_contraction_consistency(bb: BeliefBase, phi: Belief) -> bool:
    # Consistency: B ÷ phi should not derive both an atom and its negation.
    # We check all atoms explicitly because Bot() is not handled by the clause extractor in logicalEntailment.py.
    contracted = contract(bb, phi)
    for atom in _collect_atoms(contracted):
        if entails(contracted, atom) and entails(contracted, Negation(atom)):
            return False
    return True


def check_contraction_extensionality(bb: BeliefBase, phi: Belief, psi: Belief) -> bool:
    # Extensionality: if phi ≡ psi then B ÷ phi = B ÷ psi
    # Logically equivalent formulas must produce identical contractions. Assumes the caller passes genuinely equivalent phi and psi.
    c1 = contract(bb, phi)
    c2 = contract(bb, psi)
    return set(c1.get_beliefs()) == set(c2.get_beliefs())


# ==============================================================
# AGM Revision Postulate Checks
# ==============================================================

def check_revision_success(bb: BeliefBase, phi: Belief, priority: int = 1) -> bool:
    # Success: phi ∈ Cn(B * phi)
    revised = revise(bb, phi, priority)
    return entails(revised, phi)


def check_revision_inclusion(bb: BeliefBase, phi: Belief, priority: int = 1) -> bool:
    # Inclusion: B * phi ⊆ B + phi
    revised = revise(bb, phi, priority)
    expanded = expand(bb, phi, priority)
    return set(revised.get_beliefs()).issubset(set(expanded.get_beliefs()))


def check_revision_vacuity(bb: BeliefBase, phi: Belief, priority: int = 1) -> bool:
    # Vacuity: if ¬phi ∉ Cn(B) then B * phi = B + phi
    if not entails(bb, Negation(phi)):
        revised = revise(bb, phi, priority)
        expanded = expand(bb, phi, priority)
        return set(revised.get_beliefs()) == set(expanded.get_beliefs())
    return True   # ¬phi IS entailed — vacuity places no constraint here


def check_revision_consistency(bb: BeliefBase, phi: Belief, priority: int = 1) -> bool:
    # Consistency: if phi is consistent then B * phi is consistent.
    phi_bb = BeliefBase()
    phi_bb.add(phi, priority)
    phi_atoms = _collect_atoms(phi_bb)
    for atom in phi_atoms:
        if entails(phi_bb, atom) and entails(phi_bb, Negation(atom)):
            return True   # phi itself is inconsistent — postulate places no constraint

    revised = revise(bb, phi, priority)
    for atom in _collect_atoms(revised):
        if entails(revised, atom) and entails(revised, Negation(atom)):
            return False
    return True


def check_revision_extensionality(bb: BeliefBase, phi: Belief, psi: Belief, priority: int = 1) -> bool:
    # Extensionality: if phi ≡ psi then B * phi = B * psi
    r1 = revise(bb, phi, priority)
    r2 = revise(bb, psi, priority)
    for belief in r1.get_beliefs():
        if not entails(r2, belief):
            return False
    for belief in r2.get_beliefs():
        if not entails(r1, belief):
            return False
    return True






if __name__ == "__main__":
    print("=" * 60)
    print("  BELIEF REVISION ENGINE — Part 3 & 4: Contraction and Expansion")
    print("=" * 60)


    b = Atom("b")    # Tweety is a bird
    f = Atom("f")    # Tweety can fly
    r = Atom("r")    # It is raining  (unrelated — used for vacuity tests)

    bb = BeliefBase()
    bb.add(b,      priority=1)   # weak: easily given up
    bb.add(b >> f, priority=3)   # strong rule: harder to give up

    print("\nInitial belief base:")
    print(bb)

    print("\n--- Entailment checks ---")
    print(f"  B ⊢ f?  (inferred, not stored directly)  {entails(bb, f)}")   # True
    print(f"  B ⊢ b?  (stored directly)                {entails(bb, b)}")   # True
    print(f"  B ⊢ r?  (not in B at all)                {entails(bb, r)}")   # False

    # --- Expansion ---
    print("\n--- Expansion: B + r  (new compatible belief, priority 2) ---")
    bb_expanded = expand(bb, r, priority=2)
    print(bb_expanded)

    print("--- Expansion: B + b  (b already in B — no change) ---")
    print(expand(bb, b))

    # --- Contraction ---
    print("\n--- Contraction: B ÷ f ---")
    print("  f is only inferred, so we must drop b or (b>>f) to stop entailing f.")
    print("  b has priority 1, (b>>f) has priority 3 — so b is sacrificed.")
    bb_contracted = contract(bb, f)
    print(bb_contracted)
    print(f"  B ÷ f  ⊢ f?  {entails(bb_contracted, f)}")     # False — success

    print("\n--- Contraction: B ÷ r  (vacuous — r ∉ Cn(B), base unchanged) ---")
    print(contract(bb, r))

    # --- Revision ---
    print("\n--- Revision: B * ¬f  (Levi identity: contract f, then add ¬f) ---")
    print("  After adding ¬f, the rule (b>>f) and ¬f together entail ¬b.")
    print("  Learning Tweety cannot fly leads us to conclude Tweety is not a bird.")
    bb_revised = revise(bb, Negation(f), priority=2)
    print(bb_revised)
    print(f"  B * ¬f  ⊢ ¬b?  {entails(bb_revised, Negation(b))}")   # True

    print("\n--- Revision: B * r  (vacuous — ¬r ∉ Cn(B), equals expansion) ---")
    print(revise(bb, r, priority=2))

    # equivalents used for extensionality tests
    ff  = Negation(Negation(f))           # ~~f  ≡  f
    nff = Negation(Negation(Negation(f))) # ~~~f ≡ ¬f

    print("\n--- AGM Contraction Postulate Checks (B ÷ f) ---")
    print(f"  Success       B÷f ⊬ f:               {check_contraction_success(bb, f)}")
    print(f"  Inclusion     B÷f ⊆ B:               {check_contraction_inclusion(bb, f)}")
    print(f"  Vacuity       B÷r = B  (r∉Cn(B)):    {check_contraction_vacuity(bb, r)}")
    print(f"  Consistency   B÷f consistent:         {check_contraction_consistency(bb, f)}")
    print(f"  Extensionality f vs ~~f same result:  {check_contraction_extensionality(bb, f, ff)}")

    print("\n--- AGM Revision Postulate Checks (B * ¬f) ---")
    nf = Negation(f)
    print(f"  Success       ¬f ∈ Cn(B*¬f):         {check_revision_success(bb, nf)}")
    print(f"  Inclusion     B*¬f ⊆ B+¬f:           {check_revision_inclusion(bb, nf)}")
    print(f"  Vacuity       B*r = B+r  (¬r∉Cn(B)): {check_revision_vacuity(bb, r)}")
    print(f"  Consistency   B*¬f consistent:        {check_revision_consistency(bb, nf)}")
    print(f"  Extensionality ¬f vs ~~~f same conseq:{check_revision_extensionality(bb, nf, nff)}")

    print("\nAll postulates should be True.")
