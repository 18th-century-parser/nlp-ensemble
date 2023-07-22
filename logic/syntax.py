from pathlib import Path

import aiofiles
import aiohttp

from stanza import Pipeline
from stanza.utils.conll import CoNLL

from bs4 import BeautifulSoup

from misc.util import get_temp_file_path
from misc.config import Paths


class Syntax:
    def __init__(self):
        self._pipeline = Pipeline("ru", depparse_batch_size=500, depparse_model_path=str(Paths.syntax_model))

    async def process_text(self, text: str) -> Path:
        document = self._pipeline(text)
        CoNLL.write_doc2conll(document, conllu_path := get_temp_file_path("conllu"))

        return conllu_path

    async def process_text_from_file(self, path: Path) -> Path:
        async with aiofiles.open(path, "r", encoding="utf-8") as file:
            return await self.process_text(await file.read())

    @staticmethod
    async def search(conllu_path: Path, lemma: str | None, dependencies: list[str]) -> list[str]:
        def is_row_matched(row: str) -> bool:
            items = row.split("\t")

            return (
                    ((lemma.lower() in items[2].lower()) if lemma else True) and
                    ((items[7] in dependencies) if dependencies else True)
            )

        async with aiofiles.open(conllu_path, "r", encoding="utf-8") as file:
            sentence_blocks = map(lambda block: block.split("\n"), (await file.read()).strip().split("\n\n"))

        matched_blocks = filter(lambda block: any(filter(is_row_matched, block[2:])), sentence_blocks)

        return list(map(lambda block: block[0][9:], matched_blocks))

    @staticmethod
    async def visualization_html(path: Path) -> str:
        async with aiofiles.open(path, "rb") as file:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        "https://urd2.let.rug.nl/~kleiweg/conllu/bin/form",
                        data={"conllu": await file.read()},
                        headers={
                            "Content-Type": "application/octet-stream"
                        }
                ) as response:
                    soup = BeautifulSoup(
                        (await response.text()).replace("../../", "https://urd2.let.rug.nl/~kleiweg/"),
                        "lxml"
                    )

                    soup.find("div", id="top").extract()
                    for tag in soup.find_all("div", class_="udcontrol"):
                        tag.extract()

                    return str(soup)


syntax = Syntax()
