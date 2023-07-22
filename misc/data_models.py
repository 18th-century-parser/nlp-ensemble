from enum import Enum
from pydantic import BaseModel


class PartOfSpeech(str, Enum):
    noun = "S"
    verb = "V"
    adjective = "A"
    adverb = "ADV"
    pronoun_adjective = "APRO"
    pronoun_noun = "SPRO"
    number = "NUM"
    ordinal_number = "ANUM"
    preposition = "PR"
    conjunction = "CONJ"
    particle = "PART"
    interjection = "INTJ"
    pronominal_adverb = "ADVPRO"
    composite_part = "COM"


class Number(str, Enum):
    singular = "ед"
    plural = "мн"


class Gender(str, Enum):
    masculine = "муж"
    feminine = "жен"
    neuter = "сред"


class NounCase(str, Enum):
    nominative = "им"
    genitive = "род"
    dative = "дат"
    accusative = "вин"
    instrumental = "твор"
    prepositional = "пр"
    partitive = "парт"
    locative = "местн"
    vocative = "зват"


class VerbTime(str, Enum):
    past = "прош"
    present = "наст"
    future = "непрош"


class VerbType(str, Enum):
    participle = "прич"
    gerund = "деепр"
    infinitive = "инф"
    indicative = "изъяв"
    imperative = "пов"


class AdjectiveForm(str, Enum):
    full = "полн"
    short = "кр"
    possessive = "притяж"


class OtherFeatures(str, Enum):
    personal_name = "имя"
    surname = "фам"
    patronymic = "отч"
    geographical_name = "гео"
    masculine_and_feminine = "мж"
    informal = "разг"
    abbreviation = "сокр"
    obsolete = "устар"
    obscene = "обсц"
    awkward_form = "затр"
    distorted_form = "искаж"
    rare = "редк"
    introduction_word = "вводн"
    predicate = "прдк"


class WordForm(BaseModel):
    part_of_speech: PartOfSpeech | None = None
    number: Number | None = None
    gender: Gender | None = None
    noun_case: NounCase | None = None
    verb_time: VerbTime | None = None
    verb_type: VerbType | None = None
    adjective_form: AdjectiveForm | None = None
    other_features: list[OtherFeatures] = []


class LetterRange(BaseModel):
    left: str
    right: str
