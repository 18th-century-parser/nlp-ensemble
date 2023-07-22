import re

from pymongo import MongoClient
from pymongo.errors import OperationFailure

from misc.data_models import (
    PartOfSpeech, Number, Gender, NounCase, VerbTime, VerbType, AdjectiveForm, OtherFeatures, WordForm, LetterRange
)

pattern = re.compile(r'(?<!^)(?=[A-Z])')

general_enums = {
    enum: pattern.sub('_', enum.__name__).lower()
    for enum in (PartOfSpeech, Number, Gender, VerbTime, VerbType, AdjectiveForm)
}
list_value_enums = {
    enum: pattern.sub('_', enum.__name__).lower()
    for enum in (NounCase, OtherFeatures)
}  # would have a list[str] value type in the database


class Database:
    def __init__(self):
        self._client = MongoClient("localhost", 27017)
        self._db = self._client.get_database("data")

    @staticmethod
    def __prepare_tags(tags: list[str]) -> dict[str, str | list[str]]:
        result = {}

        for tag in tags:
            for enum, enum_shake_case_name in general_enums.items():
                try:
                    enum(tag)
                    result[enum_shake_case_name] = tag
                    break
                except ValueError:
                    continue
            else:
                for enum, enum_shake_case_name in list_value_enums.items():
                    try:
                        enum(tag)

                        if enum_shake_case_name in result.keys():
                            result[enum_shake_case_name].append(tag)
                        else:
                            result[enum_shake_case_name] = [tag]

                        break
                    except ValueError:
                        continue

        return result

    def get_collections(self) -> list[str]:
        return sorted(self._db.list_collection_names())

    def new_collection(self, collection_name: str, data: dict[str, dict[str, ...]]) -> None:
        prepared_data = []
        for lemma, lemma_data in data.items():
            lemma_occurrences = lemma_data.pop("occurrences")
            lemma_data.pop("other forms")

            for token, token_data in lemma_data.items():
                if token.strip() == "":
                    continue

                token_data = token_data["info"]  # ...

                for i in range(token_occurrences_count := len(token_data["index"])):
                    prepared_data.append(
                        {
                            "token": token.upper(),
                            "lemma": lemma.upper(),
                            "token_occurrences_count": token_occurrences_count,
                            "lemma_occurrences_count": lemma_occurrences,
                            "sentence": token_data["seq"][i].strip().replace("  ", " "),
                            "sentence_index": token_data["index"][i],
                            "tags": self.__prepare_tags(token_data["tags"][i])
                        }
                    )

        if prepared_data:
            self._db.get_collection(collection_name).insert_many(prepared_data)

    def search_by_token(self, token: str, collection_name: str) -> list[dict]:
        if collection_name not in self.get_collections():
            return []

        return list(
            self._db.get_collection(collection_name).find(
                {"token": token.upper()} if token else {}, {'_id': 0}
            ).sort("token")
        )

    def search_by_lemma(self, lemma: str, collection_name: str) -> list[dict]:
        if collection_name not in self.get_collections():
            return []

        return list(
            self._db.get_collection(collection_name).find(
                {"lemma": lemma.upper()} if lemma else {}, {'_id': 0}
            ).sort("token")
        )

    def search_by_word_form(self, word_form: WordForm, letter_range: LetterRange, collection_name: str) -> list[dict]:
        if collection_name not in self.get_collections():
            return []

        if letter_range.left == "ё" and letter_range.right == "ё":
            letter_range_regex = "ё"
        elif letter_range.left == "ё":
            letter_range_regex = f"ж-{letter_range.right.lower()}ё"
        elif letter_range.right == "ё":
            letter_range_regex = f"{letter_range.left.lower()}-её"
        elif ord(letter_range.left) <= ord("е") < ord(letter_range.right):
            letter_range_regex = f"{letter_range.left.lower()}-{letter_range.right.lower()}ё"
        else:
            letter_range_regex = f"{letter_range.left.lower()}-{letter_range.right.lower()}"

        query = {
            f"tags.{key}": value.value
            for key, value in filter(
                lambda pair: pair[1] is not None,
                filter(lambda pair: type(pair[1]) in general_enums, word_form.model_dump().items())
            )
        }
        query.update(
            {
                "token": {"$regex": fr"^[{letter_range_regex}][а-яё]*$", "$options": "i"},
                "lemma": {"$regex": fr"^[{letter_range_regex}][а-яё]*$", "$options": "i"},
                "tags.other_features": {
                    "$all": list(map(lambda elem: elem.value, word_form.other_features))
                } if word_form.other_features else None
            }
        )
        if word_form.noun_case:
            query.update({"tags.noun_case": word_form.noun_case.value})

        try:
            return list(self._db.get_collection(collection_name).find(query, {'_id': False}).sort(("lemma", "token")))
        except OperationFailure:
            return []


database = Database()
