import sys

from crossword import Crossword
import generate
from generate import CrosswordCreator


class NaiveCrosswordCreator(CrosswordCreator):
    """CrosswordCreator with MRV/degree/LCV disabled, for a naive-selection baseline."""

    def select_unassigned_variable(self, assignment):
        unassigned = set(self.domains.keys()) - set(assignment.keys())
        return next(iter(unassigned))

    def order_domain_values(self, var, assignment):
        return list(self.domains[var])


def main():
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python benchmark_naive.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    crossword = Crossword(structure, words)
    creator = NaiveCrosswordCreator(crossword)
    assignment = creator.solve()

    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)

    print(f"Backtrack calls: {generate.BACKTRACK_COUNTER}")
    print(f"Words tested: {generate.WORDS_TESTED}")


if __name__ == "__main__":
    main()
