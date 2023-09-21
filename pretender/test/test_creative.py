import unittest
from pretender.creative_assistant import extract_pos  # Import the function you want to test

# Your JSON data
json_data = {
    "description": "Welcome to the treacherous world of Draconia, a land filled with danger and adventure...",
    # ... (rest of your JSON data here)
}

# Combine all the text fields into a single string
all_text = " ".join([str(value) for value in json_data.values() if isinstance(value, str)])

class TestExtractPos(unittest.TestCase):
    def test_extract_nouns(self):
        nouns = extract_pos(all_text, "NOUN")
        expected_nouns = {"world", "Draconia", "land", "adventure", "heart", "kingdom", "cave", "lair", "dragon", "realm", "journey"}
        self.assertEqual(nouns, expected_nouns)

    def test_extract_verbs(self):
        verbs = extract_pos(all_text, "VERB")
        expected_verbs = {"Welcome", "filled", "lies", "rumored", "be", "has", "been", "terrorizing", "have", "gathered", "slay", "bring", "is", "filled", "have", "emerging", "face", "save"}
        self.assertEqual(verbs, expected_verbs)

if __name__ == "__main__":
    unittest.main()
