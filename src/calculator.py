import json
import math
import pandas as pd
from datetime import datetime
from io import StringIO


class Calculator:
    CALL_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, config_path: str):
        config = json.load(open(config_path, 'r'))
        self.primetime_start = datetime.strptime(config["primetime_start"], "%H:%M:%S")
        self.primetime_end = datetime.strptime(config["primetime_end"], "%H:%M:%S")
        self.primetime_rate = config["primetime_rate"]
        self.other_rate = config["other_rate"]
        self.overtime_rate = config["overtime_rate"]
        self.overtime_limit_seconds = config["overtime_limit_seconds"]
        self.free_number = None

    @staticmethod
    def _find_most_frequent_number(df: pd.DataFrame) -> int:
        return df['phone_number'].mode().max()

    def _calculate_call_started_before_primetime(self, call_start: datetime, call_end: datetime,
                                                 call_length_secs: int) -> float:
        """
        Calculate cost of phone call which started before primetime.

        :param call_start: Datetime of call's start.
        :param call_end: Datetime of call's end.
        :param call_length_secs: Call's duration in seconds.
        :return: Cost of the call.
        """
        # Call ended before primetime
        if call_end < self.primetime_start:
            cost = math.ceil(call_length_secs / 60) * self.other_rate
        # Call ended during primetime
        elif call_end < self.primetime_end:
            pre_primetime_seconds = (self.primetime_start - call_start).seconds
            primetime_seconds = (call_end - self.primetime_start).seconds

            pre_primetime_started_minutes = math.ceil(pre_primetime_seconds / 60)
            # Subtract remaining seconds of a started minute
            primetime_started_minutes = math.ceil((primetime_seconds - (60 - pre_primetime_seconds % 60)) / 60)

            cost_pre_primetime = pre_primetime_started_minutes * self.other_rate
            cost_primetime = primetime_started_minutes * self.primetime_rate
            cost = cost_pre_primetime + cost_primetime
        # Call ended after primetime
        else:
            pre_primetime_seconds = (self.primetime_start - call_start).seconds
            primetime_seconds = (self.primetime_end - self.primetime_start).seconds
            post_primetime_seconds = (call_end - self.primetime_end).seconds

            pre_primetime_started_minutes = math.ceil(pre_primetime_seconds / 60)
            # Subtract remaining seconds of a started minute
            primetime_started_minutes = math.ceil((primetime_seconds - (60 - pre_primetime_seconds % 60)) / 60)
            post_primetime_started_minutes = math.ceil((post_primetime_seconds - (60 - primetime_seconds % 60)) / 60)

            cost_pre_primetime = pre_primetime_started_minutes * self.other_rate
            cost_primetime = primetime_started_minutes * self.primetime_rate
            cost_post_primetime = post_primetime_started_minutes * self.other_rate
            cost = cost_pre_primetime + cost_primetime + cost_post_primetime

        return cost

    def _calculate_call_started_during_primetime(self, call_start: datetime, call_end: datetime,
                                                 call_length_secs: int) -> float:
        """
        Calculate cost of phone call which started during primetime.

        :param call_start: Datetime of call's start.
        :param call_end: Datetime of call's end.
        :param call_length_secs: Call's duration in seconds.
        :return: Cost of the call.
        """
        # Call ended during primetime
        if call_end < self.primetime_end:
            cost = math.ceil(call_length_secs / 60) * self.primetime_rate
        # Call ended after primetime
        else:
            primetime_seconds = (self.primetime_end - call_start).seconds
            post_primetime_seconds = (call_end - self.primetime_end).seconds

            primetime_started_minutes = math.ceil(primetime_seconds / 60)
            # Subtract remaining seconds of a started minute
            post_primetime_started_minutes = math.ceil((post_primetime_seconds - (60 - primetime_seconds % 60)) / 60)

            cost_primetime = primetime_started_minutes * self.primetime_rate
            cost_post_primetime = post_primetime_started_minutes * self.other_rate
            cost = cost_primetime + cost_post_primetime

        return cost

    def _calculate_same_day(self, call_start: datetime, call_end: datetime) -> float:
        """
        Calculate cost of a phone call during the same day.

        :param call_start: Datetime of call's start.
        :param call_end: Datetime of call's end.
        :return: Cost of the call.
        """
        self.primetime_start = self.primetime_start.replace(day=call_start.day, month=call_start.month,
                                                            year=call_start.year)
        self.primetime_end = self.primetime_end.replace(day=call_start.day, month=call_start.month,
                                                        year=call_start.year)
        call_length_secs = (call_end - call_start).seconds - 1

        # Call started before primetime
        if call_start < self.primetime_start:
            cost = self._calculate_call_started_before_primetime(call_start, call_end, call_length_secs)

        # Call started during primetime
        elif call_start < self.primetime_end:
            cost = self._calculate_call_started_during_primetime(call_start, call_end, call_length_secs)

        # Call started and ended after primetime
        else:
            cost = math.ceil(call_length_secs / 60) * self.other_rate

        return cost

    def _calculate_different_days(self, call_start: datetime, call_end: datetime) -> float:
        """
        Calculates cost of a phone calls that spans over two days.

        :param call_start: Datetime of call's start.
        :param call_end: Datetime of call's end.
        :return: Cost of the call.
        """
        call_start_midnight = call_start.replace(hour=23, minute=59, second=59)
        call_end_midnight = call_end.replace(hour=0, minute=0, second=0)
        first_day_cost = self._calculate_same_day(call_start, call_start_midnight)
        second_day_cost = self._calculate_same_day(call_end_midnight, call_end)

        return first_day_cost + second_day_cost

    def _calculate_single_call_cost(self, phone_number: int, call_start: str, call_end: str) -> float:
        """
        Calculates cost of a single phone call.

        :param phone_number: Phone number.
        :param call_start: Datetime of call's start.
        :param call_end: Datetime of call's end.
        :return: Cost of the call.
        """
        # Promo event
        if phone_number == self.free_number:
            return 0.

        call_start = datetime.strptime(call_start, self.CALL_TIME_FORMAT)
        call_end = datetime.strptime(call_end, self.CALL_TIME_FORMAT)

        if call_end < call_start:
            raise AttributeError("Call end date is earlier than call start date.")

        if call_start.day == call_end.day:
            cost = self._calculate_same_day(call_start, call_end)
        else:
            cost = self._calculate_different_days(call_start, call_end)

        # Overtime charges
        call_length_secs = (call_end - call_start).seconds - 1
        overtime = max(call_length_secs - self.overtime_limit_seconds, 0)
        overtime_cost = math.ceil(overtime / 60) * self.overtime_rate
        cost += overtime_cost

        return cost

    def calculate(self, csv_str: str) -> [float]:
        """
        Calculates costs of all phone calls from data provided via csv file.

        :param csv_str: Content of data csv file as string.
        :return: Costs of the phone calls.
        """
        df = pd.read_csv(StringIO(csv_str), header=None, names=["phone_number", "call_start", "call_end"])
        self.free_number = self._find_most_frequent_number(df)
        costs = []

        for i, row in enumerate(df.itertuples(index=False)):
            cost = self._calculate_single_call_cost(getattr(row, "phone_number"), getattr(row, "call_start"),
                                                    getattr(row, "call_end"))
            costs.append(cost)

        return costs

    def get_free_number(self) -> int:
        return self.free_number
