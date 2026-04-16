"""
Logical Entailment using Resolution
Compatible with belief_base.py

Includes:
- CNF conversion (own implementation)
- Clause extraction
- Resolution
- Entailment
- OPTIONAL SymPy validation (for testing only)
"""

from belief_base import (
    Atom, Negation, Conjunction, Disjunction,
    Implication, Equivalence, BeliefBase
)

# ==========================
# CNF Conversion
# ==========================

def eliminate_implications(f):
    if isinstance(f, Implication):
        return Disjunction(Negation(f.left), eliminate_implications(f.right))

    if isinstance(f, Equivalence):
        a = eliminate_implications(f.left)
        b = eliminate_implications(f.right)
        return Conjunction(
            Disjunction(Negation(a), b),
            Disjunction(Negation(b), a)
        )

    if isinstance(f, Conjunction):
        return Conjunction(
            eliminate_implications(f.left),
            eliminate_implications(f.right)
        )

    if isinstance(f, Disjunction):
        return Disjunction(
            eliminate_implications(f.left),
            eliminate_implications(f.right)
        )

    if isinstance(f, Negation):
        return Negation(eliminate_implications(f.formula))

    return f


def push_negations(f):
    if isinstance(f, Negation):
        inner = f.formula

        if isinstance(inner, Negation):
            return push_negations(inner.formula)

        if isinstance(inner, Conjunction):
            return Disjunction(
                push_negations(Negation(inner.left)),
                push_negations(Negation(inner.right))
            )

        if isinstance(inner, Disjunction):
            return Conjunction(
                push_negations(Negation(inner.left)),
                push_negations(Negation(inner.right))
            )

    if isinstance(f, Conjunction):
        return Conjunction(push_negations(f.left), push_negations(f.right))

    if isinstance(f, Disjunction):
        return Disjunction(push_negations(f.left), push_negations(f.right))

    return f


def distribute(f):
    if isinstance(f, Disjunction):
        A = distribute(f.left)
        B = distribute(f.right)

        if isinstance(A, Conjunction):
            return Conjunction(
                distribute(Disjunction(A.left, B)),
                distribute(Disjunction(A.right, B))
            )

        if isinstance(B, Conjunction):
            return Conjunction(
                distribute(Disjunction(A, B.left)),
                distribute(Disjunction(A, B.right))
            )

        return Disjunction(A, B)

    if isinstance(f, Conjunction):
        return Conjunction(distribute(f.left), distribute(f.right))

    return f


def to_cnf(f):
    f = eliminate_implications(f)
    f = push_negations(f)
    f = distribute(f)
    return f


# ==========================
# Clause Extraction
# ==========================

def extract_clauses(f):
    clauses = []

    def get_literals(node):
        if isinstance(node, Disjunction):
            return get_literals(node.left) | get_literals(node.right)

        if isinstance(node, Negation):
            return {("~", node.formula.name)}

        if isinstance(node, Atom):
            return {("", node.name)}

        raise ValueError(f"Unexpected node in clause: {node}")

    def split(node):
        if isinstance(node, Conjunction):
            split(node.left)
            split(node.right)
        else:
            clauses.append(get_literals(node))

    split(f)
    return clauses


# ==========================
# Resolution
# ==========================

def resolve(ci, cj):
    resolvents = []

    for lit in ci:
        complementary = ("~", lit[1]) if lit[0] == "" else ("", lit[1])

        if complementary in cj:
            new_clause = (ci - {lit}) | (cj - {complementary})
            resolvents.append(new_clause)

    return resolvents


def resolution(clauses):
    clauses = list(clauses)

    while True:
        new = []

        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                resolvents = resolve(clauses[i], clauses[j])

                if set() in resolvents:
                    return True

                new.extend(resolvents)

        if all(r in clauses for r in new):
            return False

        clauses.extend(new)


# ==========================
# Entailment
# ==========================

def entails(belief_base: BeliefBase, query):
    clauses = []

    for belief in belief_base.get_beliefs():
        cnf = to_cnf(belief)
        clauses.extend(extract_clauses(cnf))

    neg_query = Negation(query)
    cnf_query = to_cnf(neg_query)
    clauses.extend(extract_clauses(cnf_query))

    return resolution(clauses)


# ==========================
# 🔍 OPTIONAL SYMPY TESTING
# ==========================

def belief_to_sympy(f):
    from sympy import symbols
    from sympy.logic.boolalg import And, Or, Not, Implies, Equivalent

    if isinstance(f, Atom):
        return symbols(f.name)

    if isinstance(f, Negation):
        return Not(belief_to_sympy(f.formula))

    if isinstance(f, Conjunction):
        return And(belief_to_sympy(f.left), belief_to_sympy(f.right))

    if isinstance(f, Disjunction):
        return Or(belief_to_sympy(f.left), belief_to_sympy(f.right))

    if isinstance(f, Implication):
        return Implies(belief_to_sympy(f.left), belief_to_sympy(f.right))

    if isinstance(f, Equivalence):
        return Equivalent(belief_to_sympy(f.left), belief_to_sympy(f.right))

    raise ValueError(f"Unknown formula: {f}")


def compare_with_sympy(formula):
    from sympy.logic.boolalg import to_cnf as sympy_to_cnf
    from sympy import simplify_logic

    sympy_expr = belief_to_sympy(formula)
    sympy_cnf = sympy_to_cnf(sympy_expr, simplify=True)

    my_cnf = to_cnf(formula)
    my_sympy = belief_to_sympy(my_cnf)

    equivalent = simplify_logic(sympy_cnf ^ my_sympy) == False

    print("\n======================")
    print(f"Formula: {formula}")
    print(f"SymPy CNF: {sympy_cnf}")
    print(f"My CNF:    {my_cnf}")
    print(f"Equivalent? {'✅ YES' if equivalent else '❌ NO'}")

    return equivalent


# ==========================
# MAIN TESTING
# ==========================

if __name__ == "__main__":
    print("=" * 50)
    print("ENTAILMENT + TEST DEMO")
    print("=" * 50)

    p = Atom("p")
    q = Atom("q")
    r = Atom("r")

    bb = BeliefBase()
    bb.add(p >> q)
    bb.add(p)

    print("\nBelief Base:")
    print(bb)

    print("\nEntailment tests:")
    print("Does KB entail q?", entails(bb, q))  # True
    print("Does KB entail r?", entails(bb, r))  # False

    print("\nCNF Validation (SymPy):")
    compare_with_sympy(p >> q)
    compare_with_sympy((p >> q) & p)
    compare_with_sympy((p >> q) & (q >> r))