from pathlib import Path
import pickle

from tqdm import tqdm

from gensim.models import Word2Vec, Phrases
from gensim.utils import simple_preprocess

from misc.config import ngram_min_count, similarity_scale, Paths


class Semantics:
    def __init__(self):
        self._model = Word2Vec.load(str(Paths.semantics_model))

        with open(Paths.semantics_source, "r", encoding="utf-8") as _file:
            self._source = list(map(
                lambda line: simple_preprocess(line),
                filter(lambda line: line, map(lambda line: line.strip(), _file.readlines()))
            ))

        _bigram_phrases = Phrases(self._source, min_count=ngram_min_count, delimiter=" ")
        _trigram_phrases = Phrases(_bigram_phrases[self._source], min_count=ngram_min_count, delimiter=" ")

        self._bigrams = set()
        self._trigrams = set()

        for sentence in tqdm(self._source, desc="semantics first init"):
            for bigram in _bigram_phrases[sentence]:
                if len(_parts := bigram.split(" ")) == 2:
                    self._bigrams.add(" ".join(map(lambda word: word.split("_")[0], _parts)))
            for trigram in _trigram_phrases[_bigram_phrases[sentence]]:
                if len(_parts := trigram.split(" ")) == 3:
                    self._trigrams.add(" ".join(map(lambda word: word.split("_")[0], _parts)))

        self._bigrams = list(self._bigrams)
        self._trigrams = list(self._trigrams)

    def most_similar(self, add: list[str], subtract: list[str], amount: int) -> dict[str, float]:
        coefficient = 3 if add[0][-1] == "V" else 2
        return dict(
            sorted(
                map(
                    lambda pair: (pair[0], similarity_scale(float(pair[1]), coefficient)),
                    self._model.wv.most_similar(positive=add, negative=subtract, topn=amount)
                ),
                key=lambda pair: pair[1],
                reverse=True
            )
        )

    def similarity(self, word_1: str, word_2: str) -> float:
        return similarity_scale(
            float(self._model.wv.similarity(word_1, word_2)), 3 if word_1[-1] == "V" or word_2[-1] == "V" else 2
        )

    def bigrams(self, amount: int) -> list[str]:
        return self._bigrams if amount == -1 else self._bigrams[:amount]

    def trigrams(self, amount: int) -> list[str]:
        return self._trigrams if amount == -1 else self._trigrams[:amount]


if (path := Path(Paths.cache_dir, f"{Semantics.__name__.lower()}.pickle")).exists():
    with open(path, "rb") as file:
        semantics = pickle.load(file)

else:
    semantics = Semantics()

    with open(path, "wb") as file:
        pickle.dump(semantics, file)
