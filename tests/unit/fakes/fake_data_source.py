#!/usr/bin/python3

# fake_data_source.py
# Date:  20/07/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """


class FakeBinaryDataSource(BinaryDataSource):

    def __init__(self):
        super().__init__("bongo", "bongo")

    def _fetch(self) -> bytes:
        return b"Bytes objects are immutable sequences of single bytes"


class FakeTabularDataSource(IndexTabularDataSource):

    def __init__(self):
        super().__init__("bongo", FakeIndexStore())

    def _fetch(self) -> pd.DataFrame:
        d = {'col1': [1, 2, 12], 'col2': [3, 4, 13], 'col3': ['abs', 'qwe', 'bongo']}
        return pd.DataFrame(data=d)
