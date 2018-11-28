import tkinter as tk
from tkinter import filedialog
from collections import OrderedDict

import subprocess
import os
import sys
import copy

import numpy as np
import pandas as pd


class milchliste(object):
    def __init__(self):
        # spalten-nummer ab welcher die namen eingegeben werden (zähler startet bei 0!)
        self.names_start = 12
        # maximale anzahl an namen pro milchliste (für aufteilung in n milchlisten)
        self.max_names = 8

        # liste von namen für die vorrat berechnet werden soll
        self.vorratsliste = ['Cheese of the Week',
                            'Bergkäse 9',
                            'Bergkäse 3',
                            'Käsereibutter Block']


        # article numbers of additional products
        self.additional_vorrat_indexes = []

        # a dict containing required return-values from the gui
        self.returned_values = {}

        self.milchlisten_dict = {}


    def makelatexfile(self, content, filename = 'test',
                      template='milchliste', nlist=0):
        '''
        generate pdf's compile from a LaTeX file
        (!!! `pdflatex` must by found in the system to compile the pdf's !!!)

        Parameters:
        -------------
        content : pandas.DataFrame
                  a pandas DataFrame that will be converted to LaTeX input
                  using the DataFrame.to_latex() command
        filename : str
                   the full path to the pdf-file that will be generated
        template : str (default = 'milchliste')
                   the template to be used
                   (either 'checkliste', 'milchliste', or 'bestellliste')
        nlist : int
                the suffix for the list-number
                (in case more than 1 list is generated)
        '''


        if template == 'milchliste':
            latex_template = r'''
            \documentclass[11pt, a4]{article}
            \usepackage[landscape, margin=0.1in,headheight=0.0in,footskip=0.5in]{geometry}
            \usepackage{booktabs}
            \usepackage{graphicx}
            \usepackage[table]{xcolor}
            \usepackage[official]{eurosym}
            \usepackage[ngerman]{babel}
            \rowcolors{2}{gray!25}{white}
            \begin{document}
            \vspace*{\fill}
            \begin{center}
            ''' \
            + r'Milchliste ' + str(nlist + 1) + ' für KW' + str(self.returned_values['KW']) + r'\\[4ex]' + \
            r'''
            $content
            \end{center}
            \vspace*{\fill}
            \end{document}
            '''.lstrip()

            column_format = '|' + 'r|p{5cm}|' +  'r|' * (len(content.keys())-1)

        elif template == 'checkliste':
            latex_template = r'''
            \documentclass[11pt, a4]{article}
            \usepackage[portrait, margin=0.1in,headheight=0.0in,footskip=0.5in]{geometry}
            \usepackage{booktabs}
            \usepackage{graphicx}
            \usepackage[table]{xcolor}
            \usepackage[official]{eurosym}
            \usepackage[ngerman]{babel}
            \rowcolors{2}{gray!25}{white}
            \begin{document}
            \vspace*{\fill}
            \begin{center}
            ''' \
            + r'Checkliste für KW' + str(self.returned_values['KW']) + r'\\[4ex]' + \
            r'''
            $content
            \end{center}
            \vspace*{\fill}
            \end{document}
            '''.lstrip()

            column_format = '|' + 'r|p{5cm}|' + 'r|'*3 + \
                            'p{2.3cm}|' + 'p{1.3cm}|' + 'l|'

        elif template == 'bestellliste':
            latex_template = r'''
            \documentclass[11pt, a4]{article}
            \usepackage[portrait, margin=0.1in,headheight=0.0in,footskip=0.5in]{geometry}
            \usepackage{booktabs}
            \usepackage{graphicx}
            \usepackage[table]{xcolor}
            \usepackage[official]{eurosym}
            \usepackage[ngerman]{babel}
            \rowcolors{2}{gray!25}{white}
            \begin{document}
            \vspace*{8ex}
            \begin{center}
            ''' \
            + r'Bioparadeis Bestellung KW' + str(self.returned_values['KW']) + r'\\[4ex]' + \
            r'''
            $content
            \end{center}
            \vspace*{\fill}
            \end{document}
            '''.lstrip()

            column_format = '|' + 'r|' * 2

        table = content.to_latex(na_rep='',
                                bold_rows=False,
                                index=True,
                                column_format = column_format)

        # tabelle in latex-template einfügen
        latexfile = latex_template.replace('$content', table)

        # komische latex-symbole (wegen newline in cotw) entfernen
        latexfile = latexfile.replace('\\textbackslashr', '')
        latexfile = latexfile.replace('\\textbackslashn', '')

        # namen um 90 grad drehen zum platzsparen
        for i in self.milchlisten_dict['names']:
            latexfile = latexfile.replace(i, '\\rotatebox{90}{' + i + '}')

        # umlaute für latex aufbereiten
        latexfile = latexfile.replace('ö', '\"o')
        latexfile = latexfile.replace('ä', '\"a')
        latexfile = latexfile.replace('ü', '\"u')

        #  euro symbol für latex aufbereiten
        latexfile = latexfile.replace('€', '\euro')

        try:
            os.remove(os.path.join(self.returned_values['foldername'], "test.tex"))
        except OSError:
            pass

        with open(os.path.join(self.returned_values['foldername'], filename) + '.tex', "x", encoding='utf-8') as text_file:
            text_file.write(latexfile)

        #subprocess.call('pdflatex ' + os.path.join(*self.returned_values['foldername'].split('/'), filename) + '.tex', shell=True)

        subprocess.call(['pdflatex',
                         '-output-directory',
                         self.returned_values['foldername'],
                         os.path.join(self.returned_values['foldername'], filename)])

        try:
            os.remove(os.path.join(self.returned_values['foldername'], filename + '.tex'))
            os.remove(os.path.join(self.returned_values['foldername'], filename + '.aux'))
            os.remove(os.path.join(self.returned_values['foldername'], filename + '.log'))
        except OSError:
            pass


    def read_list(self):
        if 'foldername' in self.returned_values:
            currpath = self.returned_values['foldername']
        else:
            currpath = input('Input folder-path: ')

        # eine liste aller dateien finden die im ordner liegen
        allfiles = os.listdir(currpath)

        # csv-datei finden
        csvnum = 0
        for file in allfiles:
            if file.endswith('.csv'):
                csvfilename = file
                csvnum += 1
                assert csvnum <=1, 'There is more than one csv-file in the folder'

        # csv-datei als pandas-dataframe einlesen (als strings!)
        fulllist = pd.read_csv(os.path.join(currpath, csvfilename),
                               header=1, skiprows=3, decimal=b',', dtype=str)
        # format article numbers to 6 digits
        fulllist['Art. Nr.:'] = fulllist['Art. Nr.:'].str.zfill(6)
        # namen der besteller
        names_all = []
        for i in fulllist.keys()[self.names_start:]:
            if 'Unnamed' not in i:
                names_all += [i]

        # titel der produkt-beschreibungs spalten
        titles = []
        for i in fulllist.keys()[:self.names_start]:
            if 'Unnamed' not in i:
                titles += [i]

        # set all names columns to float (replacing , with .)
        # display a warning and stop if something goes wrong
        for key in names_all:
            try:
                fulllist[key] = fulllist[key].replace({',': '.'}, regex=True).apply(pd.to_numeric)
            except Exception:
                ex_type, ex_value, ex_traceback = sys.exc_info()
                from tkinter import messagebox
                errormessage = 'Es gibt ein Problemchen mit den Einträgen von ' + key + ': \n\n' \
                               + str(ex_value)
                messagebox.showerror("Upsi",
                                    errormessage)
                return False


        # boolean array um alle zeilen die keine bestellungen (oder 0 werte) enthalten zu entfernen
        # alle produkte in der vorratliste bleiben erhalten!
        #entries_nan = ~np.array(list(map(np.all, fulllist[names_all].isnull().values)))
        entries = ~np.array(list(map(np.all, (fulllist[names_all].isnull() | (fulllist[names_all] == 0)).values)))   #
        entries = np.logical_or(entries, fulllist['Art. Nr.:'].isin(self.additional_vorrat_indexes).values)


        # falls jemand einen namen eingetragen hat, aber nichts bestellt hat,
        # -> namen von liste entfernen
        names = []
        for i, name in enumerate(names_all):
            if not np.all(fulllist[entries][name].isnull()):
                names += [name]

        # zeilen auswählen die bestellungen enthalten
        orders = fulllist[entries][titles + names]

        # artikel-nummern mit führenden 0 formatieren
        orders['Art. Nr.:'] = orders['Art. Nr.:'].apply(lambda x: str(x).zfill(6))

        # artikelnummer als index setzen
        orders = orders.set_index('Art. Nr.:')
        titles.remove('Art. Nr.:')

        # summe der bestellungen berechnen
        sumorders = pd.DataFrame(orders[names].apply(np.sum, axis=1).apply(np.round, decimals=2),
                                 columns=['Bestellmenge (excl. Vorrat)'])

        # Art. Nr. für vorratsprodukte
        vorrats_index = [fulllist['Art. Nr.:'].loc[fulllist['Produkt'].apply(lambda x: str(x).find(vorratsname) !=-1)].get_values()[0] for vorratsname in self.vorratsliste]

        # TODO
        vorrats_index += self.additional_vorrat_indexes

        # bestellmengen für vorratsliste (cotw menge wird vom spreadsheet genommen)
        vorratsmenge = [float(fulllist['Menge'].loc[fulllist['Art. Nr.:'] == vorrats_index[0]]),
                        1.,
                        1.,
                        1.5
                        ]

        if len(self.additional_vorrat_indexes) > 0:
            vorratsmenge += [1.] * len(self.additional_vorrat_indexes)


        # vorrats artikel-nummern mit führenden 0 formatieren
        vorrats_index = list(map(lambda x: x.zfill(6), vorrats_index))

        vorrats_bestellmengen = dict(zip(vorrats_index, vorratsmenge))

        self.milchlisten_dict = {'fulllist' : fulllist,
                                 'titles' : titles,
                                 'names' : names,
                                 'orders' : orders,
                                 'sumorders' : sumorders,
                                 'vorrats_index' : vorrats_index,
                                 'vorrats_bestellmengen' : vorrats_bestellmengen}

        return True#fulllist, titles, names, orders, sumorders, vorrats_index, vorrats_bestellmengen


    def milchlisten_erzeugen(self):
        '''
        Parameters:
        --------------
        currpath : string
                   path to the folder where the files are located
        '''
        assert len(self.milchlisten_dict) != 0; 'you must call read_list first!'

        # copy results so that they don't get affected by vorrats-calculations
        milchlisten_dict = copy.deepcopy(self.milchlisten_dict)
        returned_values = copy.deepcopy(self.returned_values)

        # ------------------------ vorräte

        if 'KW' in returned_values:
            # if KW is provided by the gui, use it
            KW = returned_values['KW']
        else:
            returned_values['KW'] = str(input('Aktuelle Kalenderwoche = '))
            KW = returned_values['KW']

        vorratlist = []
        for i in milchlisten_dict['vorrats_index']:
            if i in milchlisten_dict['orders'].index:
                curr_order = milchlisten_dict['sumorders'].loc[i].values[0]
                while True:
                    if dict(zip(milchlisten_dict['vorrats_index'], self.vorratsliste + self.additional_vorrat_indexes))[i] in returned_values:
                        x = float(returned_values[dict(zip(milchlisten_dict['vorrats_index'], self.vorratsliste + self.additional_vorrat_indexes))[i]])
                    else:
                        print(milchlisten_dict['orders']['Produkt'].loc[i] + '  ((mindest-)Bestellmenge: ' + str(milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
                        print('Aktuelle Bestellung:   ', curr_order)
                        x = float(input('Vorrat = '))

                    #if not ((x + curr_order) / vorrats_bestellmengen[i]).is_integer():
                    # this can result in unwanted behaviour as in 2.3 + (-0.3)
                    if not np.round((x + curr_order) / milchlisten_dict['vorrats_bestellmengen'][i], 3).is_integer():
                        print("Vorrat passt nicht zur Mindestbestellmenge (Bestellmenge: "
                              + str(milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
                        continue
                    else:
                        break

                print('Bestellung incl. Vorrat:   ', curr_order + x, '\n\n')
                vorratlist += [[i, x]]
            else:
                print(milchlisten_dict['fulllist']['Produkt'].loc[milchlisten_dict['fulllist']['Art. Nr.:']==i] + '  ((mindest-)Bestellmenge: ' + str(milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
                print('Aktuelle Bestellung:   NIX')
                while True:
                    #x = float(input('Vorrat = '))
                    x = float(returned_values[dict(zip(milchlisten_dict['vorrats_index'], self.vorratsliste + self.additional_vorrat_indexes))[i]])

                    #if not ((x) / vorrats_bestellmengen[i]).is_integer():
                    if not np.round((x) / milchlisten_dict['vorrats_bestellmengen'][i], 3).is_integer():
                        print("Vorrat passt nicht zur Mindestbestellmenge (Bestellmenge: "
                              + str(milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
                        continue
                    else:
                        break

                print('Vorratsbestellung:   ', x, '\n\n')
                vorratlist += [[i, x]]


        vorrat = pd.DataFrame(vorratlist, columns=['Art. Nr.:', 'Vorrat (in kg)'])
        vorrat = vorrat.set_index('Art. Nr.:')

        # -----------------------------

        # bioparadeis bestellung
        # bestellmengen + vorräte
        sumvorratorders = milchlisten_dict['sumorders'].combine_first(vorrat).sum(axis=1)
        sumvorratorders = pd.DataFrame(sumvorratorders, columns=['Bestellmenge'])

        # bestellliste
        bestellliste = sumvorratorders.copy()

        # vorratswahren in stück-mengen umrechnen
        for i in vorrat.index:
            bestellliste.loc[i] = bestellliste.loc[i]/milchlisten_dict['vorrats_bestellmengen'][i]

        # checkliste
        checklisttitles = milchlisten_dict['orders'][milchlisten_dict['titles']].copy()

        # ----------------------- 9 monatiger bergkäse
        try:
            # Art. Nr. in spreadsheet für 9 monatigen bergkäse
            berg_9_artnr = milchlisten_dict['fulllist']['Art. Nr.:'].loc[milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 9') !=-1)].get_values()[0].zfill(6)

            berg_9_1kg_artnr = '393014'
            berg_9_1kg_nettopreis = 14.1

            berg_9_4kg_artnr = '393013'
            berg_9_4kg_nettopreis = 14.06

            # separate bergkäsebestellung in 4kg und 1kg stücke
            if bestellliste.at(berg_9_artnr, 'Bestellmenge') >= 4:
                berg_9_4kg = bestellliste.at(berg_9_artnr, 'Bestellmenge')//4
                berg_9_1kg = bestellliste.at(berg_9_artnr, 'Bestellmenge')%4
            else:
                berg_9_4kg = 0.
                berg_9_1kg = bestellliste.at(berg_9_artnr, 'Bestellmenge')

            berg_9_4kg_info = milchlisten_dict['fulllist'][milchlisten_dict['titles'] + ['Art. Nr.:']].loc[milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 9') !=-1)]
            berg_9_4kg_info['Produkt'] = 'Bergkäse 9 Mon. 4kg Stück'
            berg_9_4kg_info['Art. Nr.:'] = berg_9_4kg_artnr
            berg_9_4kg_info['Netto'] = str(berg_9_4kg_nettopreis)
            berg_9_4kg_info['Brutto'] = str(round(berg_9_4kg_nettopreis*1.1, 2))
            berg_9_4kg_info = berg_9_4kg_info.set_index('Art. Nr.:')

            berg_9_1kg_info = milchlisten_dict['fulllist'][milchlisten_dict['titles'] + ['Art. Nr.:']].loc[milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 9') !=-1)]
            berg_9_1kg_info['Produkt'] = 'Bergkäse 9 Mon. 1kg Stück'
            berg_9_1kg_info['Art. Nr.:'] = berg_9_1kg_artnr
            berg_9_1kg_info['Netto'] = str(berg_9_1kg_nettopreis)
            berg_9_1kg_info['Brutto'] = str(round(berg_9_1kg_nettopreis*1.1, 2))
            berg_9_1kg_info = berg_9_1kg_info.set_index('Art. Nr.:')

            # artikelnummer von bergkäse 9 monate korrigieren
            try:
                berg_9_vorrat = vorrat.at(berg_9_artnr, 'Vorrat (in kg)')
                vorrat = vorrat.drop(berg_9_artnr)

                berg_9_bestellung = milchlisten_dict['sumorders'].loc[berg_9_artnr]
                milchlisten_dict['sumorders'] = milchlisten_dict['sumorders'].drop(berg_9_artnr)

                bestellliste = bestellliste.drop(berg_9_artnr)

                checklisttitles = checklisttitles.drop(berg_9_artnr)
            except Exception:
                pass

            # vorrat und bestellmenge zu bestelltem produkt schreiben (1k bevorzugt)
            if berg_9_1kg > 0 or berg_9_vorrat < 0:
                vorrat.loc[berg_9_1kg_artnr] = berg_9_vorrat
                milchlisten_dict['sumorders'].loc[berg_9_1kg_artnr] = berg_9_bestellung
            elif berg_9_4kg > 0:
                vorrat.loc[berg_9_4kg_artnr] = berg_9_vorrat
                milchlisten_dict['sumorders'].loc[berg_9_4kg_artnr] = berg_9_bestellung


            if berg_9_1kg > 0 or berg_9_vorrat < 0:
                bestellliste.loc[berg_9_1kg_artnr] = berg_9_1kg
                checklisttitles.loc[berg_9_1kg_artnr] = berg_9_1kg_info.loc[berg_9_1kg_artnr]

            if berg_9_4kg > 0:
                bestellliste.loc[berg_9_4kg_artnr] = berg_9_4kg
                checklisttitles.loc[berg_9_4kg_artnr] = berg_9_4kg_info.loc[berg_9_4kg_artnr]



        except Exception:
            pass
        # ----------------------- 3 monatiger bergkäse

        try:
            # Art. Nr. in spreadsheet für 3 monatigen bergkäse
            berg_3_artnr = milchlisten_dict['fulllist']['Art. Nr.:'].loc[milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 3') !=-1)].get_values()[0].zfill(6)

            berg_3_1kg_artnr = '393004'
            berg_3_1kg_nettopreis = 11.85

            berg_3_4kg_artnr = '393003'
            berg_3_4kg_nettopreis = 11.81

            # separate bergkäsebestellung in 4kg und 1kg stücke
            if bestellliste.at(berg_3_artnr, 'Bestellmenge') >= 4:
                berg_3_4kg = bestellliste.at(berg_3_artnr, 'Bestellmenge')//4
                berg_3_1kg = bestellliste.at(berg_3_artnr, 'Bestellmenge')%4
            else:
                berg_3_4kg = 0.
                berg_3_1kg = bestellliste.at(berg_3_artnr, 'Bestellmenge')

            berg_3_4kg_info = milchlisten_dict['fulllist'][milchlisten_dict['titles'] + ['Art. Nr.:']].loc[milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 3') !=-1)]
            berg_3_4kg_info['Produkt'] = 'Bergkäse 3 Mon. 4kg Stück'
            berg_3_4kg_info['Art. Nr.:'] = berg_3_4kg_artnr
            berg_3_4kg_info['Netto'] = str(berg_3_4kg_nettopreis)
            berg_3_4kg_info['Brutto'] = str(round(berg_3_4kg_nettopreis*1.1, 2))
            berg_3_4kg_info = berg_3_4kg_info.set_index('Art. Nr.:')

            berg_3_1kg_info = milchlisten_dict['fulllist'][milchlisten_dict['titles'] + ['Art. Nr.:']].loc[milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 3') !=-1)]
            berg_3_1kg_info['Produkt'] = 'Bergkäse 3 Mon. 1kg Stück'
            berg_3_1kg_info['Art. Nr.:'] = berg_3_1kg_artnr
            berg_3_1kg_info['Netto'] = str(berg_3_1kg_nettopreis)
            berg_3_1kg_info['Brutto'] = str(round(berg_3_1kg_nettopreis*1.1, 2))
            berg_3_1kg_info = berg_3_1kg_info.set_index('Art. Nr.:')

            # artikelnummer für bergkäse 3 monate korrigieren
            try:
                berg_3_vorrat = vorrat.at(berg_3_artnr, 'Vorrat (in kg)')
                vorrat = vorrat.drop(berg_3_artnr)

                berg_3_bestellung = milchlisten_dict['sumorders'].loc[berg_3_artnr]
                milchlisten_dict['sumorders'] = milchlisten_dict['sumorders'].drop(berg_3_artnr)

                bestellliste = bestellliste.drop(berg_3_artnr)

                checklisttitles = checklisttitles.drop(berg_3_artnr)
            except Exception:
                pass

            # vorrat zu bestelltem produkt schreiben (1k bevorzugt)
            if berg_3_1kg > 0 or berg_3_vorrat < 0:
                vorrat.loc[berg_3_1kg_artnr] = berg_3_vorrat
                milchlisten_dict['sumorders'].loc[berg_3_1kg_artnr] = berg_3_bestellung
            elif berg_3_4kg > 0:
                vorrat.loc[berg_3_4kg_artnr] = berg_3_vorrat
                milchlisten_dict['sumorders'].loc[berg_3_4kg_artnr] = berg_3_bestellung


            if berg_3_1kg > 0 or berg_3_vorrat < 0:
                bestellliste.loc[berg_3_1kg_artnr] = berg_3_1kg
                checklisttitles.loc[berg_3_1kg_artnr] = berg_3_1kg_info.loc[berg_3_1kg_artnr]

            if berg_3_4kg > 0:
                bestellliste.loc[berg_3_4kg_artnr] = berg_3_4kg
                checklisttitles.loc[berg_3_4kg_artnr] = berg_3_4kg_info.loc[berg_3_4kg_artnr]

        except Exception:
            pass

        # %%

        bestellliste = bestellliste.sort_index()

        bestellliste = bestellliste.apply(lambda x: np.round(x, 2))

        # produkte die bestellmenge 0 haben exkludieren (kann passieren wenn negativ-vorrat bestellt worden ist)
        bestellliste = bestellliste.loc[bestellliste['Bestellmenge']!=0]

        #bestellliste_plot = render_mpl_table(bestellliste.fillna(''), font_size=10, col_width=2, title_height=0.02, rotation=0)
        #bestellliste_plot.text(x=0.2, y=0.9, s='Bioparadeis Bestellung KW' + KW, fontsize=16)
        #bestellliste_plot.savefig(os.path.join(currpath, 'bestellliste.pdf'))

        # astype(object) wird benötigt damit integer im latex-file nicht als float dargestellt werden (1 statt 1.0)
        self.makelatexfile(bestellliste.astype(object),
                      'Bioparadeis_Bestellung_KW' + str(KW),
                      template='bestellliste')


        # anzahl der milchlisten
        n_lists = len(milchlisten_dict['names'])//self.max_names + 1

        # milchlisten erstellen
        for i, names_choice in enumerate(np.array_split(milchlisten_dict['names'], n_lists)):

            # boolean array für zeilen die bestellungen enthalten
            entries_i = ~np.array(list(map(np.all, milchlisten_dict['orders'][names_choice].isnull().values)))

            orders_i = milchlisten_dict['orders'][milchlisten_dict['titles'] + list(names_choice)]

            # zeilen auswählen die bestellungen enthalten
            orders_i = orders_i[entries_i]


        #    milchliste_plot = render_mpl_table(orders_i.fillna(''), font_size=10)
        #    milchliste_plot.savefig(os.path.join(currpath,
        #                                         'milchliste_' + str(i) + '.pdf'))
            # astype(object) wird benötigt damit integer im latex-file nicht als float dargestellt werden (1 statt 1.0)
            self.makelatexfile(orders_i.astype('object'),
                          'Milchliste_KW' + str(KW) + '_' + str(i + 1),
                          template='milchliste', nlist=i)


        checklisttitles = checklisttitles.sort_index()

        checklisttitles.pop('Produzent')
        checklisttitles.pop('Netto')
        checklisttitles.pop('Einheit')
        checklisttitles.rename({'Brutto' : 'Preis'}, axis='columns', inplace=True)

        checkliste = pd.concat([checklisttitles, milchlisten_dict['sumorders'],
                                vorrat, bestellliste], axis=1, sort=True)
        checkliste.index.name = 'Art. Nr.:'



        #checkliste_plot = render_mpl_table(checkliste.fillna(''), font_size=10)
        #checkliste_plot.savefig(os.path.join(currpath, 'checkliste.pdf'))

        # astype(object) wird benötigt damit integer im latex-file nicht als float dargestellt werden (1 statt 1.0)
        self.makelatexfile(checkliste.astype(object),
                      'Checkliste_KW' + str(KW),
                      template='checkliste')


class gui(milchliste):
    def __init__(self):
        super().__init__() # inherit init from parent class

        # initialize main window
        self.root = tk.Tk()
        self.root.title("Milchlistonator 2000")

        # initialize main frame
        self.main_frame = tk.Frame(self.root)

        # initialize bottom frame
        self.frame_0 = tk.Frame(self.root)

        # initialize a list of the total bestellmenge variables and labels
        self.tot_best_vars = []
        self.tot_best_menge_labels = []

        # initialize a list for the vorrat entry-fields
        self.vorrat_entrys = []


        # initialize a warn variable
        self.warn_variable = tk.StringVar()
        self.warn_label = tk.Label(self.frame_0, textvariable=self.warn_variable)

        # initiate a frame for additional vorrat fields
        self.add_vorrat_frame = tk.Frame(self.root)
        # textvariable for entry field of additional vorrat prodcts
        self.add_vorrat_set_var = tk.StringVar()
        self.add_vorrat_tot_vars = []


    def gui(self):
        # reset returned values
        self.returned_values = {}

        self.additional_vorrat_indexes = []

        def open_file_dialog():
            self.returned_values['foldername'] = filedialog.askdirectory()
            _ = read_callback()


        def getresult(names, variables):
            for name, var in zip(names, variables):
                self.returned_values[name] = var.get()
            return

        # add a button for file-dialog
        tk.Button(self.frame_0, text='Ordner auswählen', command=open_file_dialog).grid(row=0, column=0, padx=20)

        self.warn_variable.set('')
        self.warn_label.grid(row=0, column=2, padx=20)

        # # Additional vorrat products - variable
        # # initialize frame for additional products
        # frame_add = tk.Frame(self.root)
        # add_vorr_prod_var = tk.StringVar(value='')
        # tk.Label(frame_add, text = 'Zusätzliche vorrats-produkte (komma-getrennt!):').grid(row=0, column=0)
        # add_entry = tk.Entry(frame_add, textvariable=add_vorr_prod_var)
        # #add_entry.bind("<Return>", self.add_field)
        # add_entry.grid(row=0, column=1)
        # frame_add.pack()




        # Kalenderwochen-variable
        KW_var = tk.StringVar(value='0')
        tk.Label(self.main_frame, text = 'Aktuelle Kalenderwoche:   KW').grid(row=0, column=0 ,sticky='E')
        tk.Entry(self.main_frame, textvariable=KW_var).grid(row=0, column=1)



        # header
        #tk.Label(self.main_frame, text = 'Produktname').grid(row=1, column=0)
        #tk.Label(self.main_frame, text = 'asdf').grid(row=1, column=1)
        tk.Label(self.main_frame, text = 'Mindestbestellmenge').grid(row=1, column=2)
        tk.Label(self.main_frame, text = 'Bestellt').grid(row=1, column=3)
        tk.Label(self.main_frame, text = 'Total').grid(row=1, column=4)

        nvorrat = len(self.vorratsliste + self.additional_vorrat_indexes)

        self.vorrat_vars = [tk.StringVar(value='0') for i in range(nvorrat)]
        self.best_vars = [tk.StringVar(value='--') for i in range(nvorrat)]
        self.mind_best_vars = [tk.StringVar(value='--') for i in range(nvorrat)]
        self.tot_best_vars += [tk.StringVar(value='--') for i in range(nvorrat)]

        vorrat_labels = [tk.StringVar(value=name) for name in self.vorratsliste + self.additional_vorrat_indexes]

        for i, [name, vorrat_var, best_var, mind_best_var, tot_best_var, vorrat_label] in enumerate(zip(self.vorratsliste + self.additional_vorrat_indexes,
                                                    self.vorrat_vars,
                                                    self.best_vars,
                                                    self.mind_best_vars,
                                                    self.tot_best_vars,
                                                    vorrat_labels)):

            # add a name to each row
            tk.Label(self.main_frame, textvariable=vorrat_label).grid(row=i + 2, column=0, sticky=tk.W)

            # add an entry-cell to each row
            entry = tk.Entry(self.main_frame, textvariable = vorrat_var)
            self.vorrat_entrys += [entry]
            entry.grid(row=i + 2, column=1, padx=20)

            # add mindestbestellmenge to each row
            tk.Label(self.main_frame, textvariable = mind_best_var
                     ).grid(row=i + 2, column=2, sticky=tk.E, padx=20)
            # add bestellmenge to each row
            tk.Label(self.main_frame, textvariable = best_var
                     ).grid(row=i + 2, column=3, sticky=tk.E, padx=20)
            # add total bestellmenge to each row
            _totlabel = tk.Label(self.main_frame, textvariable = tot_best_var)
            self.tot_best_menge_labels += [_totlabel]
            _totlabel.grid(row=i + 2, column=4, sticky=tk.E, padx=20)

        self.main_frame.pack(fill='x')


        def read_callback():
            read_Q = self.read_list()
            if read_Q is False:
                self.warn_variable.set('Ordner nicht ausgewählt... Da war ein Fehler.')
                self.warn_label.config(bg='red')
                return
            else:
                self.warn_variable.set('Ordner ausgewählt!')
                self.warn_label.config(bg='green')

            # mindestbestellmengen setzen
            mind_bestellmengen=[self.milchlisten_dict['vorrats_bestellmengen'][i] for i in self.milchlisten_dict['vorrats_index']]

            vorratprod_bestellungen = []
            for i in self.milchlisten_dict['vorrats_index']:
                try:
                    vorratprod_bestellungen += [self.milchlisten_dict['sumorders'].loc[i].values.flatten()[0]]
                except:
                    vorratprod_bestellungen += [0.]

            #vorratprod_bestellungen = [self.milchlisten_dict['sumorders'].loc[i].values.flatten()[0] for i in self.milchlisten_dict['vorrats_index']]

            for i, [mind, best] in enumerate(zip(mind_bestellmengen, vorratprod_bestellungen)):
                # mindest bestellmenge setzen
                self.mind_best_vars[i].set(mind)

                # bestellte menge setzen
                self.best_vars[i].set(best)

                # bestellmenge - mindestbestellmenge in das entry-feld schreiben
                if float(best) == 0.:
                    self.vorrat_vars[i].set(0.)
                elif float(best) > float(mind):
                    self.vorrat_vars[i].set(str(float(mind)*np.ceil(float(best)/float(mind)) - float(best)))
                elif float(best) <= float(mind):
                    self.vorrat_vars[i].set(str(np.round(float(mind) - float(best), 2)))

                # totale bestellung setzen
                self.tot_best_vars[i].set(str(np.round(float(self.vorrat_vars[i].get()) + float(best), 2)))
                self.tot_best_menge_labels[i].config(bg='green')
            # TODO
            for vorrat_label, add_vorrat_prod in zip(vorrat_labels, self.vorratsliste + self.additional_vorrat_indexes):
                if add_vorrat_prod in self.additional_vorrat_indexes:
                    vorrat_label.set(self.milchlisten_dict['fulllist']['Produkt'][self.milchlisten_dict['fulllist']['Art. Nr.:']==add_vorrat_prod].values[0])


        def add_vorrat(event):
            if 'foldername' not in self.returned_values:
                self.warn_variable.set('Zuerst Ordner auswählen!')
                self.warn_label.config(bg='red')
            else:
                mind_bestellmengen=[self.milchlisten_dict['vorrats_bestellmengen'][i] for i in self.milchlisten_dict['vorrats_index']]
                # totale bestellung setzen
                for i, best_ind in enumerate(self.milchlisten_dict['vorrats_index']):
                    try:
                        val = self.milchlisten_dict['sumorders'].loc[best_ind].values.flatten()[0]
                    except:
                        # if index is not in orders
                        val = '0.'

                    self.tot_best_vars[i].set(str(np.round(float(val) + float(self.vorrat_vars[i].get()), 2)))
                    if np.round(float(val) + float(self.vorrat_vars[i].get()), 2) % mind_bestellmengen[i] == 0:
                        self.tot_best_menge_labels[i].config(bg="green")
                    else:
                        self.tot_best_menge_labels[i].config(bg="red")


        for i in self.vorrat_entrys:
            i.bind("<FocusOut>", add_vorrat)
            i.bind("<Return>", add_vorrat)


        def add_field():
            '''
            add an additional vorrat product
            '''
            if 'foldername' not in self.returned_values:
                self.warn_variable.set('Zuerst Ordner auswählen!')
                self.warn_label.config(bg='red')
                return

            add_vorrat_index = self.add_vorrat_set_var.get()
            if add_vorrat_index in self.milchlisten_dict['vorrats_index']:
                self.warn_variable.set('Produkt bereits in liste!')
                self.warn_label.config(bg='red')
                return

            #add_vorrat_Qs = self.milchlisten_dict['fulllist']['Art. Nr.:']==add_vorrat_index

            zfilled_Art_Nrs = np.array([str(i).zfill(6) for i in self.milchlisten_dict['fulllist']['Art. Nr.:'].values.flatten()])
            add_vorrat_Qs = zfilled_Art_Nrs == add_vorrat_index

            if np.count_nonzero(add_vorrat_Qs) == 0:
                self.warn_variable.set('Artikelnummer nicht gefunden')
                self.warn_label.config(bg='red')
                return
            elif np.count_nonzero(add_vorrat_Qs) > 1:
                self.warn_variable.set('Idente Artikelnummern gefunden!')
                self.warn_label.config(bg='red')
                return
            else:
                self.warn_variable.set('...adding ' + add_vorrat_index)
                self.warn_label.config(bg='green')

            self.additional_vorrat_indexes += [add_vorrat_index]
            self.milchlisten_dict['vorrats_index'] += [add_vorrat_index]

            #row number of the added field
            n = len(self.tot_best_vars) + 3

            # mindestbestellmengen setzen
            # (if value can not be converted to float, use 1)
            try:
                mind_best=self.milchlisten_dict['fulllist']['Menge'][add_vorrat_Qs].values[0]
                self.milchlisten_dict['vorrats_bestellmengen'][add_vorrat_index] = float(mind_best)
            except:
                self.milchlisten_dict['vorrats_bestellmengen'][add_vorrat_index] = 1.


            # add mindestbestellmenge to each row
            add_min_best_var = tk.StringVar()
            self.mind_best_vars += [add_min_best_var]
            tk.Label(self.main_frame, textvariable = add_min_best_var
                      ).grid(row=n, column=2, sticky=tk.E, padx=20)
            # add bestellmenge to each row
            add_best_var = tk.StringVar()
            self.best_vars += [add_best_var]
            tk.Label(self.main_frame, textvariable = add_best_var
                      ).grid(row=n, column=3, sticky=tk.E, padx=20)
            # add total bestellmenge to each row
            tot_best_var = tk.StringVar()
            try:
                tot_best_var.set(self.milchlisten_dict['sumorders'].loc[add_vorrat_index].values.flatten()[0])
            except:
                tot_best_var.set('0')

            self.tot_best_vars += [tot_best_var]
            _totlabel = tk.Label(self.main_frame, textvariable = tot_best_var)
            self.tot_best_menge_labels += [_totlabel]
            _totlabel.grid(row=n, column=4, sticky=tk.E, padx=20)

            tk.Label(self.main_frame,
                      text=self.milchlisten_dict['fulllist']['Produkt'][add_vorrat_Qs].values[0]
                      ).grid(row=n, column=0, sticky=tk.W)

            # add entry-field
            vorrat_var = tk.StringVar()
            self.vorrat_vars += [vorrat_var]
            entry = tk.Entry(self.main_frame, textvariable = vorrat_var)
            self.vorrat_entrys += [entry]
            entry.bind("<Return>", add_vorrat)
            entry.bind("<FocusOut>", add_vorrat)
            entry.grid(row=n, column=1, padx=20)

            # call read_callback again to read the newly added products
            read_callback()


        # additional vorrat products
        add_vorrat_set_frame = tk.Frame(self.root)
        add_vorrat_set_entry = tk.Entry(self.main_frame, #add_vorrat_set_frame,
                                        textvariable=self.add_vorrat_set_var)
        add_vorrat_set_entry.insert(0, 'Art. Nr.')
        add_vorrat_set_entry.grid(row=6, column=0, padx=5, pady=5)

        # remove text on click
        def rem_text(event):
            add_vorrat_set_entry.delete(0, tk.END)
        def add_text(event):
            add_vorrat_set_entry.delete(0, tk.END)
            add_vorrat_set_entry.insert(0, 'Art. Nr.')

        add_vorrat_set_entry.bind("<Button-1>", rem_text)
        add_vorrat_set_entry.bind("<Return>", lambda event: add_field())
        add_vorrat_set_entry.bind('<FocusOut>', add_text)


        tk.Button(self.main_frame, #add_vorrat_set_frame,
                  text='Vorrat-Produkt hinzufügen',
                  command=add_field).grid(row=6, column=1, pady=5)

        add_vorrat_set_frame.pack()

        self.add_vorrat_frame.pack()


        def generate_files():
            # check if folder has been selected
            if 'foldername' not in self.returned_values:
                self.warn_variable.set('Zuerst Ordner auswählen!')
                self.warn_label.config(bg='red')

            else:
                # check if all orders are correct
                bestellmengen_OK = True
                mind_bestellmengen=[self.milchlisten_dict['vorrats_bestellmengen'][i] for i in self.milchlisten_dict['vorrats_index']]
                for i, best_ind in enumerate(self.milchlisten_dict['vorrats_index']):
                    try:
                        val = self.milchlisten_dict['sumorders'].loc[best_ind].values.flatten()[0]
                    except:
                        # if index is not in orders
                        val = '0.'

                    if np.round(float(val) + float(self.vorrat_vars[i].get()), 2) % mind_bestellmengen[i] != 0:
                        bestellmengen_OK = False
                        self.tot_best_menge_labels[i].config(bg="red")
                    else:
                        self.tot_best_menge_labels[i].config(bg="green")

                if bestellmengen_OK is False:
                    self.warn_variable.set('Bestellmengen passen nicht zu Mindestbestellmengen!')
                    self.warn_label.config(bg='red')
                else:
                    self.warn_variable.set('Milchlisten werden erzeugt...')
                    self.warn_label.config(bg='green')
                    self.root.update_idletasks()
                    _ = getresult(['KW'] + self.vorratsliste + self.additional_vorrat_indexes,
                                  [KW_var] + self.vorrat_vars)

                    self.milchlisten_erzeugen()


        # add a button to generate the lists
        tk.Button(self.frame_0, text='Milchlisten erzeugen',
                  command=generate_files).grid(row=0, column=1)
        self.frame_0.pack(fill='both', padx=10, pady=10)




        self.root.mainloop()

        self.root.quit()

        return self.returned_values

