#Part 1: Belief Base

"""
Propositional Logic Belief Base Implementation:
"""
class Belief:
    """
    This class has the operators overloaded to allow natural formula construction using Python syntax.
     - Negation: ~p
     - Conjunction: p & q
     - Disjunction: p | q
     - Implication: p >> q
     - Equivalence: p ^ q
    """
    def __neg__(self):
        return Negation(self)
    
    def __and__(self, other):
        return Conjunction(self, other)
    
    def __or__(self, other):
        return Disjunction(self, other)
    
    def __rshift__(self, other):
        return Implication(self, other)
    
    def __xor__(self, other):
        return Equivalence(self, other)
    
    def __eq__(self, other):
        return type(self) == type(other) and str(self) == str(other)
    
    def __hash__(self):
        return hash(str(self))
    

class Atom(Belief): # this is a basic propositional variable (e.g., "p", "q", "r")
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Negation(Belief):
    def __init__(self, formula):
        self.formula = formula
    def __repr__(self):
        return f"~{self.formula}"

class Conjunction(Belief):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} & {self.right})"
    
class Disjunction(Belief):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} | {self.right})"

class Implication(Belief):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} -> {self.right})"
    
class Equivalence(Belief):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} <-> {self.right})"

class Bot(Belief):
    def __repr__(self):
        return "⊥"


"""
The Belief base:
"""
class BeliefBase:
    """
    Stores a set of propositional logic formulas (beliefs) with priorities.
    """
    def __init__(self):
        self.beliefs = []

    
    def add(self, belief, priority = 1): # adding a new belief with a priority (default is 1)
        if self.contains(belief):
            print(f"Belief '{belief}' already exists in the belief base. Skipping addition.")
            return
        self.beliefs.append((belief, priority))
        self.beliefs.sort(key=lambda x: x[1]) # sort by priority (ascending order: lowest first)

    def remove(self, belief):
        before = len(self.beliefs)
        self.beliefs = [b for b in self.beliefs if b[0] != belief] # removing a belief
        after = len(self.beliefs)
        if before == after:
            print(f"Belief '{belief}' not found in the belief base.")
    
    def clear(self): # clearing all beliefs
        self.beliefs = []
        print("Belief base cleared.")
    
    def contains(self, belief) -> bool:
        return any(b == belief for b, _ in self.beliefs)
    
    def is_empty(self) -> bool:
        return len(self.beliefs) == 0
    
    def size(self) -> int:
        return len(self.beliefs)

    def get_beliefs(self) -> list:
        return [belief for belief, _ in self.beliefs]
    
    def get_priorities(self) -> dict:
        return {belief: priority for belief, priority in self.beliefs}
    
    def get_beliefs_by_priority(self, priority) -> list:
        return [belief for belief, p in self.beliefs if p == priority]
    
    def get_highest_priority_beliefs(self) -> list:
        if self.is_empty():
            return []
        highest_priority = self.beliefs[-1][1]  # last item priority = highest priority
        return [belief for belief, priority in self.beliefs if priority == highest_priority]
    
    def get_lowest_priority_beliefs(self) -> list:
        if self.is_empty():
            return []
        lowest_priority = self.beliefs[0][1]  # first item priority = lowest priority
        return [belief for belief, priority in self.beliefs if priority == lowest_priority]

    def __repr__(self):
        if self.is_empty():
            return "Belief Base is empty."
        result = "Belief Base:\n"
        for belief, priority in self.beliefs:
            result += f"  - {belief} (priority: {priority})\n"
        return result.strip()
    


#___________________________________________________________________#
#Testing the belief base implementation (This was AI generated code for testing purposes)
if __name__ == "__main__":
 
    print("=" * 50)
    print("BELIEF BASE DEMO")
    print("=" * 50)
 
    # --- Define some atoms (basic facts) ---
    p = Atom("p")   # "it is raining"
    q = Atom("q")   # "the ground is wet"
    r = Atom("r")   # "the sky is clear"
    s = Atom("s")   # "it is cold"
 
    # --- Create a belief base ---
    bb = BeliefBase()
 
    print("\n[1] Adding beliefs...")
    bb.add(Implication(p, q), priority=3)   # "if it rains, ground is wet" — high priority (physics)
    bb.add(p, priority=2)               # "it is raining" — medium priority
    bb.add(r, priority=1)               # "sky is clear" — low priority (weak belief)
    bb.add(s, priority=1)               # "it is cold" — low priority
 
    print(bb)
 
    # --- Try adding a duplicate ---
    print("\n[2] Trying to add a duplicate...")
    bb.add(p, priority=2)
    print(bb)
 
    # --- Query the belief base ---
    print("\n[3] Querying...")
    print(f"  Contains p?          {bb.contains(p)}")
    print(f"  Contains ¬p?         {bb.contains(Negation(p))}")
    print(f"  Total beliefs:       {bb.size()}")
    print(f"  Lowest priority:     {bb.get_lowest_priority_beliefs()}")
    print(f"  Highest priority:    {bb.get_highest_priority_beliefs()}")
    print(f"  All formulas:        {bb.get_beliefs()}")
    print(f"  Priority map:        {bb.get_priorities()}")
 
    # --- Remove a belief ---
    print("\n[4] Removing 'r' (sky is clear)...")
    bb.remove(r)
    print(bb)
 
    # --- Try removing something not in the base ---
    print("\n[5] Trying to remove something not in the base...")
    bb.remove(Negation(p))
 
    # --- Get beliefs by priority ---
    print("\n[6] Beliefs with priority 1:")
    print(f"  {bb.get_beliefs_by_priority(1)}")
 
    # --- Using operator overloading (natural syntax) ---
    print("\n[7] Using operator overloading for formula construction:")
    formula1 = p & q          # And(p, q)
    formula2 = p | q          # Or(p, q)
    formula3 = -p             # Neg(p)
    formula4 = p >> q         # Implies(p, q)
    formula5 = p ^ q         # Equiv(p, q)
    formula6 = Bot()         # Contradiction (⊥)
    print(f"  p & q  = {formula1}")
    print(f"  p | q  = {formula2}")
    print(f"  -p     = {formula3}")
    print(f"  p >> q = {formula4}")
    print(f"  p ^ q  = {formula5}")
    print(f"  Bot()  = {formula6}")
 
    bb.add(formula1, priority=2)
    print("\nAfter adding (p ∧ q):")
    print(bb)
 
    # --- Clear the belief base ---
    print("\n[8] Clearing the belief base...")
    bb.clear()
    print(bb)