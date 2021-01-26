import numpy as np
import pandas as pd
import os

from pandas import ExcelWriter

import DataFolderUtil
from random import random

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
        self.blank234 = constants['blank232']
        self.blank234S = constants['blank232S']

        self.chBlank230 = constants['ch_blank230']
        self.chBlank230S = constants['ch_blank230S']
        self.spBlank230 = constants['sp_blank230']
        self.spBlank230S = constants['sp_blank230S']

        self.a230232_init = constants['a230232_init']
        self.a230232_init_err = constants['a230232_init_err']

    def set_specific_constants(self, specific_constants):
        self.blk = specific_constants['Blank']
        self.yield_Th = specific_constants['Yield_Th']
        self.yield_U = specific_constants['Yield_U']
        self.gain = specific_constants['Gain']

    def set_metadata(self, metadata_path):
        self.metadata = pd.read_csv(metadata_path, sep=';', na_filter=False)
        self.metadata['Blank 234 (fg)'] = [self.blank234S if desc=='Standard' else self.blank234 for desc in self.metadata['Art der Probe']]
        self.metadata['Blank 238 (ng)'] = [self.blank238S if desc=='Standard' else self.blank238 for desc in self.metadata['Art der Probe']]
        self.metadata['Blank 232 (ng)'] = [self.blank238S if desc=='Standard' else self.blank238 for desc in self.metadata['Art der Probe']]
        self.metadata['Ch. Blank 230 (fg)'] = [self.chBlank230S if desc == 'Standard' else self.chBlank230 for desc in self.metadata['Art der Probe']]
        self.metadata['Sp. Blank 230 (fg/g)'] = [self.spBlank230S if desc == 'Standard' else self.spBlank230 for desc in self.metadata['Art der Probe']]

    def calc_concentrations(self, ratios):
        self.metadata.index = ratios.index

        placeholder_columns = 20
        results = np.empty([ratios.shape[0], placeholder_columns])
        # Ratio 238/236
        r238236 = ratios['Ratio 235/236'] * self.NR85
        r238236_err = results[:, 0] * ratios['Error (%) 235/236'] / 100

        #print(ratios)
        # 234U
        u234pgg = ( ( ratios['Ratio 234/233'] * self.tri233 * 10**-9 * self.metadata['TriSp13 (g)'] * (234/233) ) - (self.metadata['Blank 234 (fg)'] * 10**-15) ) * 10**12 / self.metadata['Einwaage (g)']
        u234pgg_err = u234pgg * ratios['Error (%) 234/233'] / 100
        u234dpmg = (u234pgg/234) * self.NA * 10**-12 * self.lambda234 / (365.2425*24*60)
        u234dpmg_err = u234dpmg * ratios['Error (%) 234/233'] / 100

        # 238U
        u238mugg = ( ( r238236 * self.tri236 * 10**-9 * self.metadata['TriSp13 (g)'] * (238/236) ) - (self.metadata['Blank 238 (ng)'] * 10**-9) ) * 10**6 / self.metadata['Einwaage (g)']
        u238mugg_err = u238mugg *  ratios['Error (%) 235/236'] / 100
        u238dpmg = (u238mugg/238.05) * self.NA * 10**-6 * self.lambda238 / (365.2425*24*60)
        u238dpmg_err = u238dpmg * ratios['Error (%) 235/236'] / 100

        # a234238
        a234238 = ratios['Ratio 234/238'] * self.lambda234/self.lambda238
        a234238_err = a234238 * ratios['Error (%) 234/238'] / 100
        a234238_corr = [a234238[i] * 2 / (a234238[i-1]+a234238[i+1]) if(0 < i < len(a234238)-1 and self.standard not in ratios.iloc[i, 0]) else a234238[i] for i in range(len(a234238))]
        a234238_corr_err = a234238_corr * ratios['Error (%) 234/238'] / 100

        # 232Th
        th232ngg = ( ( self.tri229 * 10**-9 * self.metadata['TriSp13 (g)'] * (232/229) / ratios['Ratio 229/232']) - (self.metadata['Blank 232 (ng)'] * 10**-9) ) * 10**9 / self.metadata['Einwaage (g)']
        th232ngg_err = th232ngg * ratios['Error (%) 229/232'] / 100
        th232dpmg = (th232ngg/232) * self.NA * 10**-9 * self.lambda232 / (365.2425*24*60)
        th232dpmg_err = th232dpmg * ratios['Error (%) 229/232'] / 100

        # 230Th
        th230pgg = ( ( ratios['Ratio 230/229'] * self.tri229 * 10**-9 * self.metadata['TriSp13 (g)'] * (230/229) ) - (self.metadata['Ch. Blank 230 (fg)'] * 10**-15) - (self.metadata['TriSp13 (g)'] * self.metadata['Sp. Blank 230 (fg/g)'] * 10**-15)) * 10**12 / self.metadata['Einwaage (g)']
        th230pgg_err = th230pgg * ratios['Error (%) 230/229'] / 100
        th230dpmg = (th230pgg/230) * self.NA * 10**-12 * self.lambda230 / (365.2425*24*60)
        th230dpmg_err = th230dpmg * ratios['Error (%) 230/229'] / 100

        # a230232
        a230232 = th230dpmg / th232dpmg
        a230232_err = a230232 * np.sqrt( (th230dpmg_err / th230dpmg)**2 + (th232ngg_err / th232ngg)**2 )
        a230232_corr = [a230232[i] * 2 / (a230232[i-1]+a230232[i+1]) if(0 < i <len(a230232)-1 and self.standard not in ratios.iloc[i, 0]) else a230232[i] for i in range(len(a230232))]
        a230232_corr_err = a230232_corr * np.sqrt((th230dpmg_err / th230dpmg)**2 + (th232dpmg_err / th232dpmg)**2)

        # a230238
        a230238 = th230dpmg / u238dpmg
        a230238_err = a230238 * np.sqrt((u238dpmg_err / u238dpmg) ** 2 + (th230pgg_err / th230pgg) ** 2)
        a230238_corr = [a230238[i] * 2 / (a230238[i - 1] + a230238[i + 1]) if (0 < i < len(a230238) - 1 and self.standard not in ratios.iloc[i, 0]) else a230238[i] for i in range(len(a230238))]
        a230238_corr_err = a230238_corr * np.sqrt((th230dpmg_err / th230dpmg) ** 2 + (u238dpmg_err / u238dpmg) ** 2)

        # a232238
        a232238 = th232dpmg / u238dpmg
        a232238_err = a232238 * np.sqrt((th232dpmg_err / th232dpmg)**2 + (u238dpmg_err / u238dpmg)**2)

        age_uncorr = [self.thu_alter_kombi(a230238[i], a234238[i]) for i in range(len(a230238))]
        age_uncorr_err = [self.montealter(a230238[i], a230238_err[i], a234238[i], a234238_err[i]) for i in range(len(a230238))]

        age_corr = [self.marincorr_age(a230238_corr[i], a234238_corr[i], a232238[i], self.a230232_init) for i in range(len(a230238_corr))]
        age_corr_err = [self.marincorr_age_error(a230238_corr[i], a230238_corr_err[i], a234238_corr[i], a234238_corr_err[i], a232238[i], a232238_err[i], self.a230232_init, self.a230232_init_err) for i in range(len(a230238))]

        d234U = (np.array(a234238_corr) - 1) * 1000
        d234U_err = np.array(a234238_corr_err) * 1000

        d234U_init = []
        d234U_init_err = []
        for i in range(len(age_corr)):
            if(age_corr[i] == 'Out of range'):
                d234U_init.append('/')
            else:
                d234U_init.append(((a234238_corr[i] - 1) * np.exp(self.lambda234 * age_corr[i] * 1000)) * 1000)

            if(age_corr[i] == 'Out of range' or age_corr_err[i] == 'Out of range'):
                d234U_init_err.append('/')
            else:
                d234U_init_err.append(np.sqrt((np.exp(self.lambda234 * age_corr[i] * 1000) * a234238_corr_err[i])**2 + ((a234238_corr[i]-1)*self.lambda234*np.exp(self.lambda234 * age_corr[i] * 1000) * age_corr_err[i] * 1000)**2)*1000)

        self.results = pd.DataFrame(
            {'Lab.Nr.': list(self.metadata['Lab. #']), 'Bezeich.': list(self.metadata['Bezeich.']),
             '238U': list(u238mugg), 'Fehler1': list(u238mugg_err),
             '232Th': list(th232ngg), 'Fehler2': list(th232ngg_err),
             '230Th/238U': list(a230238_corr), 'Fehler3': list(a230238_corr_err),
             '230Th/232Th': list(a230232_corr), 'Fehler4': list(a230232_corr_err),
             'd234U korr': list(d234U), 'Fehler5': list(d234U_err),
             'Alter (unkorr.)': list(age_uncorr), 'Fehler6': list(age_uncorr_err),
             'Alter (korr.)': list(age_corr), 'Fehler7': list(age_corr_err),
             'd234U (initial)': list(d234U), 'Fehler8': list(d234U_err),
             'Tiefe': list(self.metadata['Tiefe (cm)'])},
            index=ratios.iloc[:,0])

        units = pd.DataFrame({'Lab.Nr.': '', 'Bezeich.': '',
                              '238U': '(ng/g)', 'Fehler1': '(abso.)',
                              '232Th': '(ng/g)', 'Fehler2': '(abso.)',
                              '230Th/238U': '(Akt.Ver)', 'Fehler3': '(abso.)',
                              '230Th/232Th': '(Akt.Ver.)', 'Fehler4': '(abso.)',
                              'd234U korr': '(o/oo)', 'Fehler5': '(abso.) (o/oo)',
                              'Alter (unkorr.)': '(ka)', 'Fehler6': '(ka)',
                              'Alter (korr.)': '(ka)', 'Fehler7': '(ka)',
                              'd234U (initial)': '(o/oo)', 'Fehler8': '(abso.) (o/oo)',
                              'Tiefe': '(cm)'}, index=[''])


        self.results = pd.concat([self.results.iloc[:0], units, self.results[0:]])

        self.results.columns = [col_name if 'Fehler' not in str(col_name) else 'Fehler' for col_name in self.results.columns]


        writer = ExcelWriter(self.data_root_folder + '\\Results.xlsx', engine='xlsxwriter')
        self.results.to_excel(writer, 'Sheet1')
        writer.save()

    def thu_alter_kombi(self, a230238, a234238):
        xacc = 0.0001
        x1 = 0
        x2 = 1000000
        #i = 0

        fl = ((1 - np.exp(-self.lambda230 * x1)) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * x1))) - a230238
        fh = ((1 - np.exp(-self.lambda230 * x2)) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * x2))) - a230238

        if fl*fh >= 0:
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
            dxold = abs(x2-x1)
            dx = dxold

            WERT = ((1 - np.exp(-self.lambda230 * t)) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * t))) - a230238
            ABL = self.lambda230 * np.exp(-self.lambda230 * t) - (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (-self.lambda230 + self.lambda234) * np.exp((-self.lambda230 + self.lambda234) * t)

            for i in range(100):
                if((t - xh) * ABL - WERT) * ((t - xl) * ABL - WERT) >= 0:
                    dxold =dx
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
                    t = t-dx

                    if temp == t:
                        return np.round(t / 1000, 4)

                if abs(dx) < xacc:
                    return np.round(t / 1000, 4)

                WERT = ((1 - np.exp(-self.lambda230 * t)) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * t))) - a230238
                ABL = self.lambda230 * np.exp(-self.lambda230 * t) - (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (-self.lambda230 + self.lambda234) * np.exp((-self.lambda230 + self.lambda234) * t)

                if WERT < 0:
                    xl = t
                    fl = WERT
                else:
                    xh = t
                    fh = WERT

    #AV = a230238_coor
    #AU = a234238_corr
    def marincorr_age(self, a230238, a234238, a232238, a230232_init):
        xacc = 0.0001
        x1 = 0
        x2 = 1000000

        fl = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * x1) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * x1)) - a230238
        fh = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * x2) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * x2)) - a230238

        if(fl * fh >= 0):
            return "Out of range"
        else:
            if(fl < 0):
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

            WERT = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * t) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * t)) - a230238
            ABL = -self.lambda230 * (a234238 - 1) * np.exp((-self.lambda230 + self.lambda234) * t) - self.lambda230 * (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * t)

            for i in range(100):
                if((t - xh) * ABL - WERT) * ((t - xl) * ABL - WERT) >= 0:
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

                WERT = 1 + (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * t) + (a234238 - 1) * (self.lambda230 / (self.lambda230 - self.lambda234)) * (1 - np.exp(-(self.lambda230 - self.lambda234) * t)) - a230238
                ABL = -self.lambda230 * (a234238 - 1) * np.exp((-self.lambda230 + self.lambda234) * t) - self.lambda230 * (a232238 * a230232_init - 1) * np.exp(-self.lambda230 * t)

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
    def marincorr_age_error(self, a230238, a230238_err, a234238, a234238_err, a232238, a232238_err, a230232_init, a230232_init_err):

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

        fehl = 2 * np.sqrt(summe / (iter-1))

        return np.round(fehl, 10)


    iset = 0
    var1 = 0
    def gauss(self):
        if self.iset == 0:
            while(True):
                v1 = (2 * random()) - 1
                v2 = (2 * random()) - 1
                r = (v1 * v1 + v2 * v2)
                if r < 1:
                    break

            c = np.sqrt(-2 * np.log(r)/r)
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

        fehl = np.sqrt(summe / (iter-1))

        return np.round(fehl, 4)