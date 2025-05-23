"""
CSC148, Winter 2024
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
#  Copyright (c) 2019. Yuehao Huang huan1387 github@EroSkulled

import datetime
from math import ceil
from typing import Optional

from bill import Bill
from call import Call

# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """ A Term contract for a phone line

        === Public Attributes ===
        start:
             starting date for the contract
        end:
            ending date for the contract
        bill:
             bill for this contract for the last month of call records loaded
             the input dataset
        """
    start: datetime.datetime
    _end: datetime.datetime
    _curr: datetime.datetime
    bill: Optional[Bill]
    _free: int

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new TermContract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self._end = end
        self._free = TERM_MINS
        self._curr = start

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """

        bill.set_rates('TERM', TERM_MINS_COST)
        bill.add_fixed_cost(TERM_MONTHLY_FEE)
        if month == self.start.month and year == self.start.year:
            bill.add_fixed_cost(TERM_DEPOSIT)
        self._curr = datetime.date(year, month, 1)

        self.bill = bill

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        minutes = ceil(call.duration / 60.0)

        if minutes <= self._free:
            self._free -= minutes
            self.bill.add_free_minutes(minutes)
        elif self._free > 0:
            self.bill.add_free_minutes(self._free)
            self.bill.add_billed_minutes(minutes - self._free)
            self._free = 0
        else:
            self.bill.add_billed_minutes(minutes)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """

        self.start = None
        if self._curr > self._end:
            return self.bill.get_cost() - TERM_DEPOSIT
        else:
            return self.bill.get_cost()


class MTMContract(Contract):
    """ A Term contract for a phone line

    === Public Attributes ===
    start:
        starting date for the contract
    end:
        ending date for the contract
    bill:
        bill for this contract for the last month of call records loaded from
        the input dataset
    """
    start: datetime.datetime
    _end: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new MTMContract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self._end = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """

        bill.add_fixed_cost(MTM_MONTHLY_FEE)
        bill.set_rates('MTM', MTM_MINS_COST)
        self.bill = bill


class PrepaidContract(Contract):
    """ A Term contract for a phone line

    === Public Attributes ===
    start:
        starting date for the contract
    end:
        ending date for the contract
    bill:
        bill for this contract for the last month of call records loaded from
        the input dataset
    balance:
        The balance for this account (negative is credit)
    """
    start: datetime.datetime
    _end: datetime.datetime
    bill: Optional[Bill]
    _balance: int

    def __init__(self, start: datetime.date, balance: float) -> None:
        """ Create a new PrepaidContract with the <start> date, starts as inact
        """
        Contract.__init__(self, start)
        self._end = None
        self._balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """

        bill.set_rates('PREPAID', PREPAID_MINS_COST)
        try:
            self._balance = self.bill.get_cost()
        except AttributeError:
            pass
        while self._balance > -10:
            self._balance -= 25
        bill.add_fixed_cost(self._balance)
        self.bill = bill



    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return max(self.bill.get_cost(), 0)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
