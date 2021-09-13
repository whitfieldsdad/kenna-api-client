from unittest import TestCase
from kenna.error import MissingCredentialsError, InvalidCredentialsError
from kenna.authentication import API_KEY_LENGTH

import kenna.authentication


class AuthenticationTestCases(TestCase):
    def test_validate_api_key_with_empty_key(self):
        for key in ['', None]:
            with self.subTest(key=key):
                with self.assertRaises(MissingCredentialsError):
                    kenna.authentication.validate_api_key('')

    def test_validate_api_key_with_malformed_key(self):
        for key in [
            '$' * (API_KEY_LENGTH - 1),
            '$' * (API_KEY_LENGTH + 1),
        ]:
            with self.subTest(key=key, length=len(key)):
                with self.assertRaises(InvalidCredentialsError):
                    kenna.authentication.validate_api_key(key)
