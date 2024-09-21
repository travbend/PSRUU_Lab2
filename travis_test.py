import numpy as np
import queue
import pytest
from game import BoardState, GameSimulator, Rules
from search import GameStateProblem

alg = "alg"

b1 = BoardState()
b2 = BoardState()
b2.update(0, 0)

gsp = GameStateProblem(b1, b2, 0)
gsp.set_search_alg(alg)
sln = gsp.search_alg_fnc()
print(sln)