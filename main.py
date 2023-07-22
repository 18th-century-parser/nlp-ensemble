from fastapi import FastAPI, Request, UploadFile, Body
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from logic.database import database
from logic.concordancer import concordancer
from logic.syntax import syntax
from logic.semantics import semantics
from misc.data_models import WordForm, LetterRange
from misc.util import process_files, save_text


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return {"response": "I <3 Yandex"}


@app.get("/concordancer/db_names")
async def concordancer_db_names():
    return database.get_collections()


@app.post("/concordancer/files")
async def concordancer_files(files: list[UploadFile], db_name: str = Body(embed=True)):
    text_file_path = await process_files(files)

    database.new_collection(db_name, concordancer.get_forms(text_file_path))

    return {"success": True}


@app.post("/concordancer/text")
async def concordancer_text(text: str = Body(embed=True), db_name: str = Body(embed=True)):
    text_file_path = await save_text(text)

    database.new_collection(db_name, concordancer.get_forms(text_file_path))

    return {"success": True}


@app.post("/concordancer/token")
async def concordancer_token(token: str = Body(embed=True), db_name: str = Body(embed=True)):
    return database.search_by_token(token, db_name)


@app.post("/concordancer/lemma")
async def concordancer_lemma(lemma: str = Body(embed=True), db_name: str = Body(embed=True)):
    return database.search_by_lemma(lemma, db_name)


@app.post("/concordancer/form")
async def concordancer_form(form: WordForm, letter_range: LetterRange, db_name: str = Body(embed=True)):
    return database.search_by_word_form(form, letter_range, db_name)


@app.post("/syntax/files")
async def syntax_files(files: list[UploadFile]):
    text_file_path = await process_files(files)

    conllu_path = await syntax.process_text_from_file(text_file_path)

    response_html = await syntax.visualization_html(conllu_path)

    return HTMLResponse(response_html)


@app.post("/syntax/text")
async def syntax_text(request: Request):
    conllu_path = await syntax.process_text((await request.form()).get("text"))

    response_html = await syntax.visualization_html(conllu_path)

    return HTMLResponse(response_html)


@app.post("/syntax/search")
async def syntax_search(
        files: list[UploadFile], lemma: str = Body(embed=True), dependencies: str = Body(embed=True)
):
    text_file_path = await process_files(files)

    conllu_path = await syntax.process_text_from_file(text_file_path)

    return {
        "sentences": await syntax.search(
            conllu_path,
            None if lemma == "0" else lemma,
            [] if dependencies == "0" else dependencies.split(",")
        )
    }


@app.post("/semantics/most_similar")
async def semantics_most_similar(
        add: list[str] = Body(embed=True),
        subtract: list[str] = Body(embed=True),
        amount: int = Body(embed=True),
):
    try:
        return semantics.most_similar(add, subtract, amount)
    except KeyError:
        return {"error": "invalid word"}


@app.post("/semantics/similarity")
async def semantics_similarity(word_1: str = Body(embed=True), word_2: str = Body(embed=True)):
    try:
        return {"similarity": semantics.similarity(word_1, word_2)}
    except KeyError:
        return {"error": "invalid word"}


@app.post("/semantics/bigrams")
async def semantics_bigrams(amount: int = Body(embed=True)):
    return semantics.bigrams(amount)


@app.post("/semantics/trigrams")
async def semantics_trigrams(amount: int = Body(embed=True)):
    return semantics.trigrams(amount)
