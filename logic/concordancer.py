from pathlib import Path
import re

from pymystem3 import Mystem


class Concordancer:
    def __init__(self):
        self._stem = Mystem(entire_input=False)

    # noinspection PyTypeChecker
    def get_forms(self, path: Path):
        with open(path, "r", encoding="utf-8") as file:
            text = re.sub(r"\s+", " ", file.read().strip())

        sentences = filter(lambda sentence: sentence, re.split(r"[.?!]", text))
        all_forms = {}
        seq_ind = 1

        for sentence in sentences:
            a = self._stem.analyze(sentence)
            ind = 0

            for full_analysis in a:
                word = full_analysis["text"]

                try:
                    lemma = full_analysis['analysis'][0]['lex']
                    analysis = full_analysis['analysis'][0]['gr']
                except IndexError:
                    continue

                tags = []
                tmp = ""
                flag = False

                # This code is written by another person, don't judge me for it
                for i in analysis:
                    if i == '(':
                        tmp = ""
                        flag = True

                    elif i == ')':
                        tmp = tmp.replace('|', ',')
                        tmp = tmp.replace('=', ',')
                        a = tmp.split(',')
                        res = set()
                        if len(a) == 1:
                            tags.append(a[0])
                            continue
                        elif len(a) == 0:
                            continue
                        for j in a:
                            res.add(j)
                        for j in res:
                            tags.append(j)
                        flag = False
                        tmp = ""

                    if i == '=':
                        tags.append(tmp)
                        tmp = ""
                        continue

                    if i == ',' and not flag and i != ')':
                        tags.append(tmp)
                        tmp = ""

                    elif i.isalpha() or i == ',' or i == '|':
                        tmp += i

                if len(tmp) > 0:
                    tags.append(tmp)

                if all_forms.get(lemma) is None:
                    all_forms[lemma] = {}
                    all_forms[lemma]['occurrences'] = 1
                    all_forms[lemma]['other forms'] = {}
                    all_forms[lemma][word] = {}
                    all_forms[lemma][word]['info'] = {}
                    all_forms[lemma][word]['info']['tags'] = []
                    all_forms[lemma][word]['info']['seq'] = []
                    all_forms[lemma][word]['info']['index'] = []
                    all_forms[lemma][word]['info']['tags'].append(tags)
                    all_forms[lemma][word]['info']['seq'].append(sentence)
                    all_forms[lemma][word]['info']['index'].append(seq_ind)

                else:
                    if all_forms[lemma].get(word) is None:
                        all_forms[lemma][word] = {}
                        all_forms[lemma][word]['info'] = {}
                        all_forms[lemma][word]['info']['seq'] = []
                        all_forms[lemma][word]['info']['index'] = []
                        all_forms[lemma][word]['info']['tags'] = []

                    all_forms[lemma]['occurrences'] += 1
                    all_forms[lemma][word]['info']['tags'].append(tags)
                    all_forms[lemma][word]['info']['seq'].append(sentence)
                    all_forms[lemma][word]['info']['index'].append(seq_ind)

                ind += 1

            seq_ind += 1

        return all_forms


concordancer = Concordancer()
