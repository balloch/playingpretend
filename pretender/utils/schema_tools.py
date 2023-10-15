import json
import spacy


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    from spacy.cli import download

    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# Define a function to check if a verb is active
def is_active_verb(token):
    return (
        token.pos_ == "VERB" and
        "pass" not in [child.dep_ for child in token.children]
    )

# Define functions to extract unique parts of speech from text
def extract_basic_pos(text, pos_type):
    doc = nlp(text)
    pos_set = set()

    for token in doc:
        if token.pos_ == pos_type:
            pos_set.add(token.text)

    return pos_set


# Define a recursive function to extract unique nouns, active verbs, and named entities from text
def extract_pos_and_entities(text):
    doc = nlp(text)
    nouns = set()
    verbs = set()
    proper_nouns = set()

    for token in doc:
        if token.pos_ == "NOUN":
            nouns.add(token.text)
        elif is_active_verb(token):
            verbs.add(token.text)
        if token.ent_type_ in {"PERSON", "ORG", "GPE"}:
            proper_noun = token.text
            # Check if the current token is part of a multi-token entity
            while token.i + 1 < len(doc) and doc[token.i + 1].ent_iob_ == 'I':
                token = doc[token.i + 1]
                proper_noun += " " + token.text
            proper_nouns.add(proper_noun)

    for child in doc:
        # if child.text.lower() == "description":
        #     continue  # Skip the "description" field to avoid processing it again

        if isinstance(text, str):
            try:
                child_json = json.loads(text)
                for key, value in child_json.items():
                    if isinstance(value, str):
                        nested_nouns, nested_verbs, nested_proper_nouns = extract_pos_and_entities(value)
                        nouns.update(nested_nouns)
                        verbs.update(nested_verbs)
                        proper_nouns.update(nested_proper_nouns)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                nested_nouns, nested_verbs, nested_proper_nouns = extract_pos_and_entities(item)
                                nouns.update(nested_nouns)
                                verbs.update(nested_verbs)
                                proper_nouns.update(nested_proper_nouns)
            except json.JSONDecodeError:
                pass

    return nouns, verbs, proper_nouns


def extract_pos_json(json_dict, pos_type=None):
    """
    :return: the nouns, verbs, and proper nouns in the JSON data
    """
    json_text = json.dumps(json_dict, ensure_ascii=False)
    # all_text = " ".join([str(value) for value in json_dict.values() if isinstance(value, str)])
    # return extract_pos_and_entities(all_text, pos_type)
    return extract_pos_and_entities(json_text)



