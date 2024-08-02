from typing import List

from fastapi import FastAPI
from selenium import webdriver
from bs4 import BeautifulSoup
import logging

time_ids = {
    "indicative": {
        "present": "temps0",
        "present_perfect": "temps100",
        "imperfect": "temps6",
        "pluperfect": "temps106",
        "simple_past": "temps12",
        "past_perfect": "temps112",
        "future": "temps18",
        "past_future": "temps118"
    },
    "subjunctive": {
        "present": "temps24",
        "imperfect": "temps30",
        "pluperfect": "temps130",
        "past": "temps124"
    },
    "conditional": {
        "present": "temps36",
        "first_past": "temps136",
        "second_past": "temps137"
    },
    "imperative": {
        "present": "temps42",
        "past": "temps142",
    },
    "participle": {
        "present": "temps46",
        "past": "temps255",
    },
    "infinitive": {
        "present": "temps253",
        "past": "temps254",
    },
    "gerund": {
        "present": "temps251",
        "past": "temps221",
    },
}

URL = "https://leconjugueur.lefigaro.fr/french/"

options = webdriver.FirefoxOptions()
options.add_argument('--incognito')
options.add_argument('--headless')

driver = webdriver.Firefox(options=options)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FrenchVerbsScraper')

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/verb/{word}")
async def get_word(word: str):
    page_url = URL + "verb/" + word
    logger.info(f"Page URL: {page_url}")

    driver.get(page_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    word_forms = {}
    for sentence_type in time_ids.keys():
        word_forms[sentence_type] = get_sentence_type_times(soup, sentence_type)
    return {word: word_forms}


def get_sentence_type_times(soup: BeautifulSoup, sentence_type: str):
    logger.info("Getting Indicative")
    sentence = {}
    for time in time_ids[sentence_type]:
        logger.info(f"Getting: {time}")
        sentence[time] = get_words_for_time(soup, sentence_type, time)
    return sentence


def get_words_for_time(soup: BeautifulSoup, sentence_type: str, time: str) -> List[str]:
    time_element = soup.find(id=time_ids[sentence_type][time]).parent

    children = [child for child in time_element.children]
    children = children[1:]

    standardized_children = []
    current_child = ""
    for child in children:
        if child.text == "":
            standardized_children.append(current_child)
            current_child = ""
        else:
            current_child += child.text
    if current_child != "":
        standardized_children.append(current_child)

    return standardized_children
