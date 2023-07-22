from pathlib import Path
import re

from xml.etree import ElementTree
from xml.etree.ElementTree import Element


prefix = "{http://www.gribuser.ru/xml/fictionbook/2.0}"

ugly_space = chr(160)


def text_from_element(element: Element) -> str:
    return re.sub(
        r"\[\w+]\s",
        "",
        " ".join(
            map(
                lambda text: "\n".join(
                    map(
                        lambda line: line.strip(),
                        text.replace(ugly_space, " ").split("\n")
                    )
                ),
                element.itertext()
            )
        )
    )


def process_fb2(path: Path) -> str:
    parser = ElementTree.XMLParser(encoding="utf-8")
    tree = ElementTree.parse(path, parser=parser)
    root = tree.getroot()
    body: Element = root.find("body") or root.find(f"{prefix}body")

    return "\n".join(
        map(
            lambda section: "\n".join(map(text_from_element, section.findall("p") + section.findall(f"{prefix}p"))),
            body.findall("section") + body.findall(f"{prefix}section")
        )
    ).replace("\n\n", "\n")
