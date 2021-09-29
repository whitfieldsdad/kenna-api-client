import hodgepodge.types
import os

INTEGRATION_TESTS_ENABLED = hodgepodge.types.str_to_bool(os.getenv("ENABLE_INTEGRATION_TESTS", False))
