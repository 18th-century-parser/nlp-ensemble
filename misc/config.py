from pathlib import Path
from tempfile import gettempdir
import math


ngram_min_count = 40

pi_30 = math.pi / 30


def similarity_scale(x: float, coefficient: int) -> float:
    return min(max((x - pi_30) * coefficient, -1), 1)


class Paths:
    syntax_model = Path("resources/syntax.pt")
    semantics_model = Path("resources/semantics.model")
    semantics_source = Path("resources/semantics_source.txt")

    temp_dir = Path(gettempdir(), "kruase")
    cache_dir = Path("cache")


for dir in (Paths.temp_dir, Paths.cache_dir):
    dir.mkdir(exist_ok=True)
