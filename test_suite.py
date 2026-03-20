# Pytest Test Suite - #63 (15 RTC)

import pytest

def test_basic():
    assert True

def test_string():
    assert 'hello' in 'hello world'

def test_list():
    assert len([1, 2, 3]) == 3

def test_dict():
    d = {'a': 1, 'b': 2}
    assert d['a'] == 1

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
