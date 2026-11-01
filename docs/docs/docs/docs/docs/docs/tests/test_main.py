import unittest
from main import clean_phone, clean_email, check_facts, clean, is_valid


class CleanerTests(unittest.TestCase):
    def test_phone_removes_formatting(self):
        self.assertEqual(clean_phone("+91 98400-12345"), "9840012345")

    def test_phone_rejects_wrong_length(self):
        self.assertIsNone(clean_phone("987654321"))

    def test_email_lowercase(self):
        self.assertEqual(clean_email("PRIYA.K@gmail.com"), "priya.k@gmail.com")

    def test_email_words_not_completed(self):
        self.assertIsNone(clean_email("priya at gmail dot com"))

    def test_fact_check_rejects_invented_phone(self):
        checked, issues = check_facts(
            "Name: Asha, phone 987654321, email asha@gmail.com",
            {"name": "Asha", "phone": "9999999999", "email": "asha@gmail.com",
             "year": 2, "branch": "CSE"}
        )
        self.assertIsNone(checked["phone"])
        self.assertTrue(any("phone failed" in issue for issue in issues))

    def test_invalid_year_flagged(self):
        cleaned = clean({"name": "Asha", "phone": "9876543210",
                         "email": "asha@gmail.com", "year": 5, "branch": "CSE"})
        valid, reasons = is_valid(cleaned)
        self.assertFalse(valid)
        self.assertIn("missing or invalid year", reasons)


if __name__ == "__main__":
    unittest.main()
