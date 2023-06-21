import pytest
from src.calculator import Calculator


class TestCalculator:
    CONFIG = "config/config.json"
    CALCULATOR = Calculator(CONFIG)

    VALID_TEST_DATA = """
    420599759670,2022-01-23 7:59:50,2022-01-23 8:00:48
    420599759670,2022-01-23 7:59:50,2022-01-23 8:00:48
    420599759671,2022-01-23 7:59:50,2022-01-23 8:00:48
    420599759672,2022-01-23 8:00:00,2022-01-23 8:01:00
    420599759673,2022-01-23 16:00:00,2022-01-23 16:06:00
    420599759674,2022-01-23 16:00:00,2022-01-23 16:01:02
    """

    INVALID_TEST_DATA = """
    420599759670,2022-01-23 7:59:50,2022-01-23 8:00:48
    420599759670,2022-01-23 7:59:50,2022-01-23 8:00:48
    420599759671,2022-01-23 7:59:50,2022-01-23 7:00:48
    """

    EXPECTED_COSTS = [0., 0., 0.5, 1.0, 3.2, 1.0]

    def test_valid_data(self):
        computed_costs = self.CALCULATOR.calculate(self.VALID_TEST_DATA)
        assert computed_costs == self.EXPECTED_COSTS

    def test_invalid_data(self):
        with pytest.raises(AttributeError):
            self.CALCULATOR.calculate(self.INVALID_TEST_DATA)
