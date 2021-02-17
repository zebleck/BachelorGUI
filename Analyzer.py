import numpy as np
import pandas as pd
import os

import openpyxl
from pandas import ExcelWriter

import DataFolderUtil
from random import random

import ExcelFormatter


class Analyzer:
    def __init__(self):
        self.data_root_folder = None

    def set_path(self, path):
        self.data_root_folder = path
        self.standard = DataFolderUtil.findStandardNumber(path)

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

        self.lambda232 = constants['l232']
        self.lambda234 = constants['l234']
        self.lambda238 = constants['l238']
        self.lambda230 = constants['l230']

        self.tri236 = constants['tri236']
        self.tri233 = constants['tri233']
        self.tri229 = constants['tri229']

        self.blank234 = constants['blank234']
        self.blank234S = constants['blank234S']
        self.blank238 = constants['blank238']
        self.blank238S = constants['blank238S']
        self.blank232 = constants['blank232']
        self.blank232S = constants['blank232S']

        self.chBlank230 = constants['ch_blank230']
        self.chBlank230S = constants['ch_blank230S']
        self.spBlank230 = constants['sp_blank230']

        self.a230232_init = constants['a230232_init']
        self.a230232_init_err = constants['a230232_init_err']

        self.standardBezeich = constants['standardBezeich']
        self.standardEinwaage = constants['standardEinwaage']
        self.standardTriSp13 = constants['standardTriSp13']


    def set_specific_constants(self, specific_constants):
        self.blk = specific_constants['Blank']
        self.yield_Th = specific_constants['Yield_Th']
        self.yield_U = specific_constants['Yield_U']
        self.gain = specific_constants['Gain']
        self.tailShift = specific_constants['Tail shift']

    def set_metadata(self, metadata_path):
        standardInFile = False

        if metadata_path.endswith('.csv'):
            self.metadata = pd.read_csv(metadata_path, sep=';', na_filter=False)
            self.metadata['Tiefe'] = self.metadata.pop('Tiefe (cm)')
            self.tiefe_unit = 'cm'

            if int(self.standard) in list(self.metadata['Lab. #']):
                standardInFile = True

        elif metadata_path.endswith('.xlsx'):
            # pd.read_excel() throws an error when using in .exe
            metadata = pd.read_excel(metadata_path, sheet_name='Ergebnisse', na_filter=False, engine='openpyxl')

            rows = []
            metadata_dict = {'Lab. #': [], 'Bezeich.': [], 'Art der Probe': [], 'Mess. Dat.': [], 'Tiefe': [],
                             'Einwaage (g)': [], 'TriSp13 (g)': []}

            for idx, row in metadata.iterrows():
                if idx == 0:
                    if 'cm' in metadata.iloc[idx, 4]:
                        self.tiefe_unit = 'cm'
                    elif 'mm' in metadata.iloc[idx, 4]:
                        self.tiefe_unit = 'mm'
                try:
                    labnr = int(metadata.iloc[idx, 0])
                    if labnr == int(self.standard):
                        standardInFile = True
                    metadata_dict['Lab. #'].append(labnr)
                    metadata_dict['Bezeich.'].append(metadata.iloc[idx, 1])
                    metadata_dict['Art der Probe'].append(metadata.iloc[idx, 2])
                    metadata_dict['Mess. Dat.'].append(metadata.iloc[idx, 3])
                    metadata_dict['Tiefe'].append(metadata.iloc[idx, 4])
                    metadata_dict['Einwaage (g)'].append(metadata.iloc[idx, 5])
                    metadata_dict['TriSp13 (g)'].append(metadata.iloc[idx, 6])
                except:
                    pass

            self.metadata = pd.DataFrame(metadata_dict)

        # prevents wrong date format in results file
        try:
            self.metadata['Mess. Dat.'] = self.metadata['Mess. Dat.'].dt.strftime('%d.%m.%Y')
        except:
            pass

        # fixes standard name in "Art der Probe"
        for i in range(len(self.metadata.index)):
            if self.metadata['Art der Probe'][i] == 'St.':
                self.metadata['Art der Probe'][i] = 'Standard'

        if not standardInFile:
            standardRow = pd.DataFrame(
                {'Lab. #': [int(self.standard)], 'Bezeich.': [self.standardBezeich], 'Art der Probe': ['Standard'],
                 'Mess. Dat.': [''], 'Tiefe': [''],
                 'Einwaage (g)': [self.standardEinwaage], 'TriSp13 (g)': [self.standardTriSp13]})
            for i in range(len(self.metadata)):
                self.metadata = pd.concat([self.metadata.iloc[:2*i], standardRow, self.metadata.iloc[2*i:]], ignore_index=True)
            self.metadata = pd.concat([self.metadata, standardRow], ignore_index=True)

        blank234 = [self.blank234S if desc == 'Standard' else self.blank234 for desc in self.metadata['Art der Probe']]
        blank238 = [self.blank238S if desc == 'Standard' else self.blank238 for desc in self.metadata['Art der Probe']]
        blank232 = [self.blank232S if desc == 'Standard' else self.blank232 for desc in self.metadata['Art der Probe']]
        chBlank230 = [self.chBlank230S if desc == 'Standard' else self.chBlank230 for desc in
                      self.metadata['Art der Probe']]
        spBlank230 = [self.spBlank230 for desc in self.metadata['Art der Probe']]

        self.blanks = pd.DataFrame({'Blank 234 (fg)': blank234,
                                    'Blank 238 (ng)': blank238,
                                    'Blank 232 (ng)': blank232,
                                    'Ch. Blank 230 (fg)': chBlank230,
                                    'Sp. Blank 230 (fg/g)': spBlank230})

    def calc_concentrations(self, ratios):
        self.metadata.index = ratios.index


        # Ratio 238/236
        r238236 = ratios['Ratio 235/236'] * self.NR85
        r238236_err = r238236 * ratios['Error (%) 235/236'] / 100

        # print(ratios)
        # 234U
        u234pgg = ((ratios['Ratio 234/233'] * self.tri233 * 10 ** -9 * self.metadata['TriSp13 (g)'] * (
                234.0409521 / 233.0396352)) -
                   (self.blanks['Blank 234 (fg)'] * 10 ** -15)) * 10 ** 12 / self.metadata['Einwaage (g)']
        u234pgg_err = u234pgg * ratios['Error (%) 234/233'] / 100
        u234dpmg = (u234pgg / 234) * self.NA * 10 ** -12 * self.lambda234 / (365.2425 * 24 * 60)
        u234dpmg_err = u234dpmg * ratios['Error (%) 234/233'] / 100

        # 238U
        u238mugg = ((r238236 * self.tri236 * 10 ** -9 * self.metadata['TriSp13 (g)'] * (238.0507882 / 236.045568)) -
                    (self.blanks['Blank 238 (ng)'] * 10 ** -9)) * 10 ** 6 / self.metadata['Einwaage (g)']
        u238mugg_err = u238mugg * ratios['Error (%) 235/236'] / 100
        u238dpmg = (u238mugg / 238.05) * self.NA * 10 ** -6 * self.lambda238 / (365.2425 * 24 * 60)
        u238dpmg_err = u238dpmg * ratios['Error (%) 235/236'] / 100

        # a234238
        a234238 = ratios['Ratio 234/238'] * self.lambda234 / self.lambda238
        a234238_err = a234238 * ratios['Error (%) 234/238'] / 100
        a234238_corr = [a234238[i] * 2 / (a234238[i - 1] + a234238[i + 1])
                        if (0 < i < len(a234238) - 1 and self.standard not in ratios.iloc[i, 0]) else a234238[i] for i
                        in range(len(a234238))]
        a234238_corr_err = a234238_corr * ratios['Error (%) 234/238'] / 100

        # 232Th
        th232ngg = ((self.tri229 * 10 ** -9 * self.metadata['TriSp13 (g)'] * (232.0380553 / 229.031762) / ratios[
            'Ratio 229/232']) -
                    (self.blanks['Blank 232 (ng)'] * 10 ** -9)) * 10 ** 9 / self.metadata['Einwaage (g)']
        th232ngg_err = th232ngg * ratios['Error (%) 229/232'] / 100
        th232dpmg = (th232ngg / 232) * self.NA * 10 ** -9 * self.lambda232 / (365.2425 * 24 * 60)
        th232dpmg_err = th232dpmg * ratios['Error (%) 229/232'] / 100

        # 230Th
        th230pgg = ((ratios['Ratio 230/229'] * self.tri229 * 10 ** -9 * self.metadata['TriSp13 (g)'] * (
                230.0331338 / 229.031762)) -
                    (self.blanks['Ch. Blank 230 (fg)'] * 10 ** -15) - (self.metadata['TriSp13 (g)'] * self.blanks[
                    'Sp. Blank 230 (fg/g)'] * 10 ** -15)) * 10 ** 12 / self.metadata['Einwaage (g)']
        th230pgg_err = th230pgg * ratios['Error (%) 230/229'] / 100
        th230dpmg = (th230pgg / 230) * self.NA * 10 ** -12 * self.lambda230 / (365.2425 * 24 * 60)
        th230dpmg_err = th230dpmg * ratios['Error (%) 230/229'] / 100

        # a230232
        a230232 = th230dpmg / th232dpmg
        a230232_err = a230232 * np.sqrt((th230dpmg_err / th230dpmg) ** 2 + (th232ngg_err / th232ngg) ** 2)
        a230232_corr = [a230232[i] * 2 / (a230232[i - 1] + a230232[i + 1])
                        if (0 < i < len(a230232) - 1 and self.standard not in ratios.iloc[i, 0]) else a230232[i] for i
                        in range(len(a230232))]
        a230232_corr_err = a230232_corr * np.sqrt((th230dpmg_err / th230dpmg) ** 2 + (th232dpmg_err / th232dpmg) ** 2)

        # a230238
        a230238 = th230dpmg / u238dpmg
        a230238_err = a230238 * np.sqrt((u238dpmg_err / u238dpmg) ** 2 + (th230pgg_err / th230pgg) ** 2)
        a230238_corr = [a230238[i] * 2 / (a230238[i - 1] + a230238[i + 1])
                        if (0 < i < len(a230238) - 1 and self.standard not in ratios.iloc[i, 0]) else a230238[i] for i
                        in range(len(a230238))]
        a230238_corr_err = a230238_corr * np.sqrt((th230dpmg_err / th230dpmg) ** 2 + (u238dpmg_err / u238dpmg) ** 2)

        # a232238
        a232238 = th232dpmg / u238dpmg
        a232238_err = a232238 * np.sqrt((th232dpmg_err / th232dpmg) ** 2 + (u238dpmg_err / u238dpmg) ** 2)

        # Ages

        age_uncorr = [self.thu_alter_kombi(a230238[i], a234238[i]) for i in range(len(a230238))]
        age_uncorr_err = [self.montealter(a230238[i], a230238_err[i], a234238[i], a234238_err[i]) for i in
                          range(len(a230238))]

        age_uncorr_rel_err = [age_uncorr_err[i] / age_uncorr[i] * 100
                              if age_uncorr[i] != 'Out of range' and age_uncorr_err[i] != '/' else '/' for i in
                              range(len(age_uncorr))]

        age_corr = [self.marincorr_age(a230238_corr[i], a234238_corr[i], a232238[i], self.a230232_init) for i in
                    range(len(a230238_corr))]
        age_corr_err = [self.marincorr_age_error(a230238_corr[i],
                                                 a230238_corr_err[i],
                                                 a234238_corr[i],
                                                 a234238_corr_err[i],
                                                 a232238[i],
                                                 a232238_err[i],
                                                 self.a230232_init,
                                                 self.a230232_init_err) for i in range(len(a230238))]

        age_corr_rel_err = [age_corr_err[i] / age_corr[i] * 100
                            if age_corr[i] != 'Out of range' and age_corr_err[i] != '/' else 'Out of range' for i in
                            range(len(age_corr))]

        d234U = (np.array(a234238_corr) - 1) * 1000
        d234U_err = np.array(a234238_corr_err) * 1000

        age_corr_taylor = [self.taylor_err(self.a230232_init,
                                           age_corr[i],
                                           d234U[i],
                                           a232238[i],
                                           a232238_err[i],
                                           self.a230232_init_err,
                                           a234238_corr_err[i],
                                           a230238_corr_err[i]) for i in range(len(age_corr))]

        d234U_init = []
        d234U_init_err = []
        for i in range(len(age_corr)):
            if (age_corr[i] == 'Out of range'):
                d234U_init.append('/')
            else:
                d234U_init.append(((a234238_corr[i] - 1) * np.exp(self.lambda234 * age_corr[i] * 1000)) * 1000)

            if (age_corr[i] == 'Out of range' or age_corr_err[i] == '/'):
                d234U_init_err.append('/')
            else:
                d234U_init_err.append(np.sqrt(
                    (np.exp(self.lambda234 * age_corr[i] * 1000) * a234238_corr_err[i]) ** 2 + (
                            (a234238_corr[i] - 1) * self.lambda234 * np.exp(self.lambda234 * age_corr[i] * 1000) *
                            age_corr_err[i] * 1000) ** 2) * 1000)

        cheng_corr = [age_corr[i] * 1000 - 58
                      if age_corr[i] != 'Out of range' else 'Out of range' for i in range(len(age_corr))]
        taylor_err_one_sig = [age_corr_taylor[i] / 2 * 1000
                              if age_corr_taylor[i] != '/' else '/' for i in range(len(cheng_corr))]
        two_sig_t = [taylor_err_one_sig[i] / age_corr[i] * 100
                     if taylor_err_one_sig != '/' and age_corr[i] != 'Out of range' else '/' for i in
                     range(len(age_corr))]

        # Create input sheet dataframe

        self.input = pd.concat([self.metadata, ratios], axis=1)
        self.input.drop(['dU234', 'Error dU234 (abs.)'], axis=1, inplace=True)

        input_units = ['', '', '', '', '', '', '', '', '', '', 'gem.', '(%)', 'gem.', '(%)', 'gem.+korr.', '(%)', 'gem.', '(%)', 'gem.', '(%)', '', '(%)', '', '(%)', '', '(%)']
        input_units_frame = pd.DataFrame(dict(zip(self.input.columns, input_units)), index=[''])
        self.input = pd.concat([self.input.iloc[:0], input_units_frame, self.input[0:]])

        # Create calc sheet dataframe

        self.calc = pd.DataFrame({
            'Lab. #': list(self.metadata['Lab. #']), 'Bezeich.': list(self.metadata['Bezeich.']),
            '244/233U': list(ratios['Ratio 234/233']), 'Fehler1': list(ratios['Error (%) 234/233']),
            '235/236U': list(ratios['Ratio 235/236']), 'Fehler2': list(ratios['Error (%) 235/236']),
            '238/236U': r238236, 'Fehler3': r238236_err,
            'Blank 234': self.blanks['Blank 234 (fg)'],
            '234U1': u234pgg, 'Fehler4': u234pgg_err,
            '234U2': u234dpmg, 'Fehler5': u234dpmg_err,
            'Blank 238': self.blanks['Blank 238 (ng)'],
            '238U1': u238mugg, 'Fehler6': u238mugg_err,
            '238U2': u234dpmg, 'Fehler7': u234dpmg_err,
            '234U/238U': a234238, 'Fehler8': a234238_err,
            '234U/238Ukorr': a234238_corr, 'Fehler9': a234238_corr_err,
            'Blank 232': self.blanks['Blank 232 (ng)'],
            '232Th': th232ngg, 'Fehler10': th232ngg_err,
            'A232': th232dpmg, 'Fehler11': th232dpmg_err,
            'Ch. Bl. 230': self.blanks['Ch. Blank 230 (fg)'], 'Sp. Bl. 230': self.blanks['Sp. Blank 230 (fg/g)'],
            '230Th1': th230pgg, 'Fehler12': th230pgg_err,
            '230Th2': th230dpmg, 'Fehler13': th230dpmg_err,
            'A230/232': a230232, 'Fehler14': a230232_err,
            'd234U': d234U, 'Fehler15': d234U_err,
            '230Th/238U': a230238, 'Fehler16': a230238_err,
            '230Th/238Ukorr': a230238_corr, 'Fehler17': a230238_corr_err,
            'Alter (unkorr.)': age_uncorr, 'Fehler18': age_uncorr_err, 'Fehler': age_uncorr_rel_err,
            '232Th/238U': a232238, 'Fehler20': a232238_err,
            '(230Th/232Th)': self.a230232_init, 'Fehler21': self.a230232_init_err,
            'Cheng korr.': age_corr, 'Fehler22': age_corr_err, 'Fehler23': age_corr_taylor,
            'Fehler24': age_corr_rel_err,
            'Bezeichnung': list(self.metadata['Bezeich.']), 'Tiefe': self.metadata['Tiefe'],
            'd234U (initial)': d234U_init, 'Fehler25': d234U_init_err,
            'Cheng korr': cheng_corr, 'Fehler 1σ': taylor_err_one_sig, '2sig/t': two_sig_t
        })

        calc_units = ['', '', 'gem.+korr.', '(abso.)', 'gem.+korr.', '(abso.)', 'gem.',
                      '(abso.)', '(fg)', '(pg/g)', '(abs.)', '(dpm/g)', '(abso.)',
                      '(ng)', '(μg/g)', '(abso.)', '(dpm/g)', '(abso.)', 'Akt. Ver.',
                      '(abso.)', 'Akt. Ver.', '(abso.)', '(ng)', '(ng/g)', '(abso.)',
                      '(dpm/g)', '(abso.)', '(fg)', '(fg/g)', '(pg/g)', '(abso.)',
                      '(dpmg/g)', '(abso.)', '', '(abso.)', '(o/oo)', '(abso.) o/oo',
                      'Akt. Ver.', '(abso.)', 'Akt.Ver.', '(abso.)', '(ka)', '(ka)', '(%)',
                      'Akt. Ver.', '(abso.)', 'Akt. Ver. initial', '(abso.)', '(ka)', '(ka)',
                      'Taylor 1. Ord.', '(%)', '', self.tiefe_unit, '(o/oo)', '(abso.) o/oo',
                      '(a BP)', '(a)', '(%)']

        #print(list(self.calc.columns), len(list(self.calc.columns)))
        #print(calc_units, len(calc_units))
        calc_units_frame = pd.DataFrame(dict(zip(self.calc.columns, calc_units)), index=[''])

        self.calc = pd.concat([self.calc.iloc[:0], calc_units_frame, self.calc[0:]])
        #print(dict(zip(self.calc.columns, calc_units)))

        # Create results sheet dataframe

        self.results = pd.DataFrame({
            'Lab. #': list(self.metadata['Lab. #']), 'Bezeich.': list(self.metadata['Bezeich.']),
            '238U': list(u238mugg), 'Fehler1': list(u238mugg_err),
            '232Th': list(th232ngg), 'Fehler2': list(th232ngg_err),
            '230Th/238U': list(a230238_corr), 'Fehler3': list(a230238_corr_err),
            '230Th/232Th': list(a230232_corr), 'Fehler4': list(a230232_corr_err),
            'd234U korr': list(d234U), 'Fehler5': list(d234U_err),
            'Alter (unkorr.)': list(age_uncorr), 'Fehler6': list(age_uncorr_err),
            'Alter (korr.)': list(age_corr), 'Fehler7': list(age_corr_err),
            'd234U (initial)': list(d234U), 'Fehler8': list(d234U_err),
            'Tiefe': list(self.metadata['Tiefe'])
        },
            index=ratios.iloc[:, 0])

        results_units = pd.DataFrame({'Lab. #': '', 'Bezeich.': '',
                                      '238U': '(ng/g)', 'Fehler1': '(abso.)',
                                      '232Th': '(ng/g)', 'Fehler2': '(abso.)',
                                      '230Th/238U': '(Akt.Ver)', 'Fehler3': '(abso.)',
                                      '230Th/232Th': '(Akt.Ver.)', 'Fehler4': '(abso.)',
                                      'd234U korr': '(o/oo)', 'Fehler5': '(abso.) (o/oo)',
                                      'Alter (unkorr.)': '(ka)', 'Fehler6': '(ka)',
                                      'Alter (korr.)': '(ka)', 'Fehler7': '(ka)',
                                      'd234U (initial)': '(o/oo)', 'Fehler8': '(abso.) (o/oo)',
                                      'Tiefe': self.tiefe_unit}, index=[''])

        self.results = pd.concat([self.results.iloc[:0], results_units, self.results[0:]])

        writer = ExcelWriter(self.data_root_folder + '\\Results.xlsx', engine='xlsxwriter')
        ExcelFormatter.format(writer, {'Input': self.input, 'Calc': self.calc, 'Results': self.results})
        writer.save()

    def thu_alter_kombi(self, a230238, a234238):

        xacc = 0.0001
        x1 = 0
        x2 = 1000000
        # i = 0

        fl = ((1 - np.exp(-self.lambda230 * x1)) + (a234238 - 1) * (
                self.lambda230 / (self.lambda230 - self.lambda234)) * (
                      1 - np.exp(-(self.lambda230 - self.lambda234) * x1))) - a230238
        fh = ((1 - np.exp(-self.lambda230 * x2)) + (a234238 - 1) * (
                self.lambda230 / (self.lambda230 - self.lambda234)) * (
                      1 - np.exp(-(self.lambda230 - self.lambda234) * x2))) - a230238

        if fl * fh >= 0:
            return "Out of range"
        else:

            if fl < 0:
                xl = x1
                xh = x2
            else:
                xh = x1
                xl = x2
                swap = fl
                fl = fh
                fh = swap

            t = 0.5 * (x1 + x2)
            dxold = abs(x2 - x1)
            dx = dxold

            WERT = ((1 - np.exp(-self.lambda230 * t)) + (a234238 - 1) * (
                    self.lambda230 / (self.lambda230 - self.lambda234)) * (
                            1 - np.exp(-(self.lambda230 - self.lambda234) * t))) - a230238
            ABL = self.lambda230 * np.exp(-self.lambda230 * t) - (a234238 - 1) * (
                    self.lambda230 / (self.lambda230 - self.lambda234)) * (
                          -self.lambda230 + self.lambda234) * np.exp((-self.lambda230 + self.lambda234) * t)

            for i in range(100):
                if ((t - xh) * ABL - WERT) * ((t - xl) * ABL - WERT) >= 0:
                    dxold = dx
                    dx = 0.5 * (xh - xl)
                    t = xl + dx

                    if abs(dx) < xacc:
                        return np.round(t / 1000, 4)
                elif abs(2 * WERT) > abs(dxold * ABL):
                    dxold = dx
                    dx = 0.5 * (xh - xl)
                    t = xl + dx

                    if abs(dx) < xacc:
                        return np.round(t / 1000, 4)
                else:
                    dxold = dx
                    dx = WERT / ABL
                    temp = t
                    t = t - dx

                    if temp == t:
                        return np.round(t / 1000, 4)

                if abs(dx) < xacc:
                    return np.round(t / 1000, 4)

                WERT = ((1 - np.exp(-self.lambda230 * t)) + (a234238 - 1) * (
                        self.lambda230 / (self.lambda230 - self.lambda234)) * (
                                1 - np.exp(-(self.lambda230 - self.lambda234) * t))) - a230238
                ABL = self.lambda230 * np.exp(-self.lambda230 * t) - (a234238 - 1) * (
                        self.lambda230 / (self.lambda230 - self.lambda234)) * (
                              -self.lambda230 + self.lambda234) * np.exp((-self.lambda230 + self.lambda234) * t)

                if WERT < 0:
                    xl = t
                    fl = WERT
                else:
                    xh = t
                    fh = WERT

    # AV = a230238_coor
    # AU = a234238_corr
    def marincorr_age(self, a230238, a234238, a232238, a230232_init):
        xacc = 0.0001
        x1 = 0
        x2 = 1000000

        fl = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * x1) + (a234238 - 1) * (
                self.lambda230 / (self.lambda230 - self.lambda234)) * (
                     1 - np.exp(-(self.lambda230 - self.lambda234) * x1)) - a230238
        fh = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * x2) + (a234238 - 1) * (
                self.lambda230 / (self.lambda230 - self.lambda234)) * (
                     1 - np.exp(-(self.lambda230 - self.lambda234) * x2)) - a230238

        if (fl * fh >= 0):
            return "Out of range"
        else:
            if (fl < 0):
                xl = x1
                xh = x2
            else:
                xh = x1
                xl = x2
                swap = fl
                fl = fh
                fh = swap

            t = 0.5 * (x1 + x2)
            dxold = abs(x2 - x1)
            dx = dxold

            WERT = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * t) + (a234238 - 1) * (
                    self.lambda230 / (self.lambda230 - self.lambda234)) * (
                           1 - np.exp(-(self.lambda230 - self.lambda234) * t)) - a230238
            ABL = -self.lambda230 * (a234238 - 1) * np.exp((-self.lambda230 + self.lambda234) * t) - self.lambda230 * (
                    a232238 * a230232_init - 1) * np.exp(-self.lambda230 * t)

            for i in range(100):
                if ((t - xh) * ABL - WERT) * ((t - xl) * ABL - WERT) >= 0:
                    dxold = dx
                    dx = 0.5 * (xh - xl)
                    t = x1 + dx

                    if abs(dx) < xacc:
                        return np.round(t / 1000, 4)
                elif abs(2 * WERT) > abs(dxold * ABL):
                    dxold = dx
                    dx = 0.5 * (xh - xl)
                    t = x1 + dx

                    if abs(dx) < xacc:
                        return np.round(t / 1000, 4)
                else:
                    dxold = dx
                    dx = WERT / ABL
                    temp = t
                    t = t - dx
                    if temp == t:
                        return np.round(t / 1000, 4)

                if abs(dx) < xacc:
                    return np.round(t / 1000, 4)

                WERT = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * t) + (a234238 - 1) * (
                        self.lambda230 / (self.lambda230 - self.lambda234)) * (
                               1 - np.exp(-(self.lambda230 - self.lambda234) * t)) - a230238
                ABL = -self.lambda230 * (a234238 - 1) * np.exp(
                    (-self.lambda230 + self.lambda234) * t) - self.lambda230 * (a232238 * a230232_init - 1) * np.exp(
                    -self.lambda230 * t)

                if WERT < 0:
                    xl = t
                    fl = WERT
                else:
                    xh = t
                    fh = WERT

    # AV = a230238
    # AU = a234238
    # AT232 = a232238
    # ATinitial = a230232_init
    def marincorr_age_error(self, a230238, a230238_err, a234238, a234238_err, a232238, a232238_err, a230232_init,
                            a230232_init_err):

        iter = 5000
        summe = 0

        felda = np.empty(iter)
        feldb = np.empty(iter)
        feldc = np.empty(iter)
        feldd = np.empty(iter)
        res = np.empty(iter)

        for i in range(iter):
            felda[i] = self.gauss() * (0.5 * a230238_err) + a230238
            feldb[i] = self.gauss() * (0.5 * a234238_err) + a234238
            feldc[i] = self.gauss() * (0.5 * a232238_err) + a232238
            feldd[i] = self.gauss() * (0.5 * a230232_init_err) + a230232_init
            result = self.marincorr_age(felda[i], feldb[i], feldc[i], feldd[i])
            if result == 'Out of range':
                return '/'
            res[i] = result
            summe = summe + res[i]

        mean = np.round(summe / iter, 4)

        summe = 0

        for i in range(iter):
            summe = summe + ((res[i] - mean) * (res[i] - mean))

        fehl = 2 * np.sqrt(summe / (iter - 1))

        return np.round(fehl, 10)

    iset = 0
    var1 = 0

    def gauss(self):
        if self.iset == 0:
            while (True):
                v1 = (2 * random()) - 1
                v2 = (2 * random()) - 1
                r = (v1 * v1 + v2 * v2)
                if r < 1:
                    break

            c = np.sqrt(-2 * np.log(r) / r)
            self.var1 = v1 * c
            self.iset = 1
            return v2 * c
        else:
            self.iset = 0
            return self.var1

    def montealter(self, a230238, a230238_err, a234238, a234238_err):
        # number of iterations
        iter = 4999

        felda = np.empty(iter)
        feldb = np.empty(iter)
        res = np.empty(iter)

        summe = 0
        for i in range(iter):
            felda[i] = self.gauss() * a230238_err + a230238
            feldb[i] = self.gauss() * a234238_err + a234238

            result = self.thu_alter_kombi(felda[i], feldb[i])
            if result == 'Out of range':
                return '/'
            res[i] = result
            summe = summe + res[i]

        mean = np.round(summe / iter, 2)

        summe = 0
        for i in range(iter):
            summe = summe + ((res[i] - mean) * (res[i] - mean))

        fehl = np.sqrt(summe / (iter - 1))

        return np.round(fehl, 4)

    # AU = self.a230232_init
    # AW = age_corr
    # AJ = d234U
    # AS = a232238
    # AT = a232238_err
    # AV = self.a230232_init_err
    # T = a234238_corr_err
    # AO = a230238_corr_err)
    def taylor_err(self, au, aw, aj, as_, at, av, t, ao):

        if aw == 'Out of range':
            return '/'
        else:
            return np.sqrt(((au * np.exp(-self.lambda230 * aw * 1000)) / (self.lambda230 * (
                np.exp(-self.lambda230 * aw * 1000) + (aj / 1000) * np.exp(
                -(self.lambda230 - self.lambda234) * aw * 1000)
                - as_ * au * np.exp(-self.lambda230 * aw * 1000)))) ** 2 * at ** 22 + (
                (as_ * np.exp(-self.lambda230 * aw * 1000)) / (
                self.lambda230 * (np.exp(-self.lambda230 * aw * 1000) +
                             (aj / 1000) * np.exp(
                -(self.lambda230 - self.lambda234) * aw * 1000) - as_ * au * np.exp(
                -self.lambda230 * aw * 1000)))) ** 2 * av ** 2 + (
                (self.lambda230 / (self.lambda230 - self.lambda234))
                * (np.exp(-(self.lambda230 - self.lambda234) * aw * 1000) - 1) / (
                   self.lambda230 * (
                   np.exp(-self.lambda230 * aw * 1000) + (aj / 1000) * np.exp(
                -(self.lambda230 - self.lambda234) * aw * 1000)
                   - as_ * au * np.exp(
                -self.lambda230 * aw * 1000)))) ** 2 * t ** 2 + (1 / (
                self.lambda230 * (np.exp(-self.lambda230 * aw * 1000) + (aj / 1000) * np.exp(
                -(self.lambda230 - self.lambda234) * aw * 1000)
                - as_ * au * np.exp(-self.lambda230 * aw * 1000)))) ** 2 * ao ** 2) / 1000
