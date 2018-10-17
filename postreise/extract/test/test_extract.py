import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import extract_data

def test():
    extract_data.extract_scenario('western_scenarioUnitTest02')
