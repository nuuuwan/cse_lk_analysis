import os
import statistics

import numpy as np
from utils import Log, TSVFile

log = Log('cse_analysis')
DATA_PATH = os.path.join('data', 'cse.tsv')
# Contains data from 1993-07-01 to 2023-08-01
# Source: https://www.investing.com/indices/cse-all-share-historical-data


def parse_float(x):
    x = x.replace(',', '')
    return float(x)


class History:
    def __init__(self, x, y):
        assert len(x) == len(y)
        self.x = x
        self.y = y

    @staticmethod
    def load():
        data = TSVFile(DATA_PATH).read()
        x = [d['Date'] for d in data]
        y = [parse_float(d['Price']) for d in data]
        return History(x, y)

    def __len__(self) -> int:
        return len(self.x)

    @property
    def n(self) -> int:
        return len(self)

    @property
    def change(self) -> float:
        return self.y[-1] - self.y[0]

    @property
    def p_change(self) -> float:
        return self.change / self.y[0]

    def expand(self, n_months: int):
        assert n_months > 0
        n_months_compressed = len(self) - n_months
        history_list = []
        for i in range(n_months_compressed):
            x2 = self.x[i: i + n_months + 1]
            y2 = self.y[i: i + n_months + 1]
            history_list.append(History(x2, y2))
        return history_list

    def get_statistics(self, n_months: int):
        history_list = self.expand(n_months)
        p_changes = [history.p_change for history in history_list]
        mean = statistics.mean(p_changes)
        stdev = statistics.stdev(p_changes)
        percentiles = [
            np.percentile(p_changes, p)
            for p in [i * 10 for i in range(0, 11)]
        ]
        return dict(mean=mean, stdev=stdev, percentiles=percentiles)


if __name__ == '__main__':
    history = History.load()
    for n_months in [1, 2, 3, 6, 12, 24, 48, 60, 120, 240]:
        stats = history.get_statistics(n_months)
        print(f'{n_months} months: {stats}')
