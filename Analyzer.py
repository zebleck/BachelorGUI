import numpy as np

class Analyzer:
    def __init__(self):
        pass

    def set_constants(self, constants):
        # spike impurities
        self.R34_33 = constants['R3433']
        self.R35_33 = constants['R3533']
        self.R30_29 = constants['R3029']

        # constants
        self.mf48 = constants['mf48']
        self.mf36 = constants['mf36']
        self.mf56 = constants['mf56']
        self.mf68 = constants['mf68']
        self.mf92 = constants['mf92']

        self.mf38 = constants['mf38']
        self.mf35 = constants['mf35']
        self.mf43 = constants['mf43']
        self.mf45 = constants['mf45']
        self.mf09 = constants['mf09']
        self.mf29 = constants['mf29']
        self.mf34 = constants['mf34']
        self.mf58 = constants['mf58']
        self.mf02 = constants['mf02']

        self.NA = constants['NA']
        self.NR85 = constants['NR85']
        self.cps = constants['cps']

        self.slope229Correction = constants['slope']

        self.lambda234 = constants['l234']
        self.lambda238 = constants['l238']
        self.lambda230 = constants['l230']

        self.tri236 = constants['tri236']
        self.tri233 = constants['tri233']
        self.tri229 = constants['tri229']

    def calc_concentrations(self, ratios):
        print(ratios.shape)
        placeholder_columns = 20
        results = np.empty([ratios.shape[0], placeholder_columns])
        # Ratio 238/236
        results[:, 0] = ratios['Ratio 235/236'] * self.NR85
        results[:, 1] = results[:, 0] * ratios['Error (%) 235/236'] / 100
        # 234U (dpm/g)
        results[:, 2] = self.tri236 * results[:, 0] * 10**-9

        print(results)