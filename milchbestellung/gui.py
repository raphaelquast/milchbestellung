import tkinter as tk
from tkinter import filedialog

import numpy as np
import pandas as pd
import subprocess
import os


class milchliste(object):
    def __init__(self):
        # initialize main window
        self.root = tk.Tk()

        # spalten-nummer ab welcher die namen eingegeben werden (zähler startet bei 0!)
        self.names_start = 12
        # maximale anzahl an namen pro milchliste (für aufteilung in n milchlisten)
        self.max_names = 8

        # liste von namen für die vorrat berechnet werden soll
        self.vorratsliste = ['Cheese of the Week',
                             'Bergkäse 9',
                             'Bergkäse 3',
                             'Käsereibutter Block']

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

        currpath = self.returned_values['foldername']
        # eine liste aller dateien finden die im ordner liegen
        allfiles = os.listdir(currpath)

        # csv-datei finden
        csvnum = 0
        for file in allfiles:
            if file.endswith('.csv'):
                csvfilename = file
                csvnum += 1
                assert csvnum <=1, 'There is more than one csv-file in the folder'

        # csv-datei als pandas-dataframe einlesen
        fulllist = pd.read_csv(os.path.join(currpath, csvfilename),
                               header=1, skiprows=3, decimal=b',')

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

        # boolean array um alle zeilen die keine bestellungen (oder 0 werte) enthalten zu entfernen
        #entries_nan = ~np.array(list(map(np.all, fulllist[names_all].isnull().values)))
        entries = ~np.array(list(map(np.all, (fulllist[names_all].isnull() | (fulllist[names_all] == 0)).values)))

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

        # Art. Nr. für cotw und butterbl3ock
        vorrats_index = [fulllist['Art. Nr.:'].loc[fulllist['Produkt'].apply(lambda x: str(x).find(vorratsname) !=-1)].get_values()[0] for vorratsname in self.vorratsliste]

        # bestellmengen für vorratsliste (cotw menge wird vom spreadsheet genommen)
        vorratsmenge = [float(fulllist['Menge'].loc[fulllist['Art. Nr.:'] == vorrats_index[0]]),
                        1.,
                        1.,
                        1.5
                        ]

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

        return fulllist, titles, names, orders, sumorders, vorrats_index, vorrats_bestellmengen


    def milchlisten_erzeugen(self):
        '''
        Parameters:
        --------------
        currpath : string
                   path to the folder where the files are located
        '''

        # ------------------------ vorräte

        KW = self.returned_values['KW']#str(input('Aktuelle Kalenderwoche = '))

        vorratlist = []
        for i in self.milchlisten_dict['vorrats_index']:
            if i in self.milchlisten_dict['orders'].index:
                curr_order = self.milchlisten_dict['sumorders'].loc[i].values[0]
                print(self.milchlisten_dict['orders']['Produkt'].loc[i] + '  ((mindest-)Bestellmenge: ' + str(self.milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
                print('Aktuelle Bestellung:   ', curr_order)
                while True:
                    #x = float(input('Vorrat = '))
                    x = float(self.returned_values[dict(zip(self.milchlisten_dict['vorrats_index'], self.vorratsliste))[i]])

                    #if not ((x + curr_order) / vorrats_bestellmengen[i]).is_integer():
                    # this can result in unwanted behaviour as in 2.3 + (-0.3)
                    if not np.round((x + curr_order) / self.milchlisten_dict['vorrats_bestellmengen'][i], 3).is_integer():
                        print("Vorrat passt nicht zur Mindestbestellmenge (Bestellmenge: "
                              + str(self.milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
                        continue
                    else:
                        break

                print('Bestellung incl. Vorrat:   ', curr_order + x, '\n\n')
                vorratlist += [[i, x]]
            else:
                print(self.milchlisten_dict['fulllist']['Produkt'].loc[self.milchlisten_dict['fulllist']['Art. Nr.:']==i] + '  ((mindest-)Bestellmenge: ' + str(self.milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
                print('Aktuelle Bestellung:   NIX')
                while True:
                    #x = float(input('Vorrat = '))
                    x = float(self.returned_values[dict(zip(self.milchlisten_dict['vorrats_index'], self.vorratsliste))[i]])

                    #if not ((x) / vorrats_bestellmengen[i]).is_integer():
                    if not np.round((x) / self.milchlisten_dict['vorrats_bestellmengen'][i], 3).is_integer():
                        print("Vorrat passt nicht zur Mindestbestellmenge (Bestellmenge: "
                              + str(self.milchlisten_dict['vorrats_bestellmengen'][i]) + ')')
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
        sumvorratorders = self.milchlisten_dict['sumorders'].combine_first(vorrat).sum(axis=1)
        sumvorratorders = pd.DataFrame(sumvorratorders, columns=['Bestellmenge'])

        # bestellliste
        bestellliste = sumvorratorders.copy()

        # vorratswahren in stück-mengen umrechnen
        for i in vorrat.index:
            bestellliste.loc[i] = bestellliste.loc[i]/self.milchlisten_dict['vorrats_bestellmengen'][i]

        # checkliste
        checklisttitles = self.milchlisten_dict['orders'][self.milchlisten_dict['titles']].copy()

        # ----------------------- 9 monatiger bergkäse
        try:
            # Art. Nr. in spreadsheet für 9 monatigen bergkäse
            berg_9_artnr = self.milchlisten_dict['fulllist']['Art. Nr.:'].loc[self.milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 9') !=-1)].get_values()[0].zfill(6)

            berg_9_1kg_artnr = '393014'
            berg_9_1kg_nettopreis = 14.1

            berg_9_4kg_artnr = '393013'
            berg_9_4kg_nettopreis = 14.06

            # separate bergkäsebestellung in 4kg und 1kg stücke
            if bestellliste.get_value(berg_9_artnr, 'Bestellmenge') >= 4:
                berg_9_4kg = bestellliste.get_value(berg_9_artnr, 'Bestellmenge')//4
                berg_9_1kg = bestellliste.get_value(berg_9_artnr, 'Bestellmenge')%4
            else:
                berg_9_4kg = 0.
                berg_9_1kg = bestellliste.get_value(berg_9_artnr, 'Bestellmenge')

            berg_9_4kg_info = self.milchlisten_dict['fulllist'][self.milchlisten_dict['titles'] + ['Art. Nr.:']].loc[self.milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 9') !=-1)]
            berg_9_4kg_info['Produkt'] = 'Bergkäse 9 Mon. 4kg Stück'
            berg_9_4kg_info['Art. Nr.:'] = berg_9_4kg_artnr
            berg_9_4kg_info['Netto'] = str(berg_9_4kg_nettopreis)
            berg_9_4kg_info['Brutto'] = str(round(berg_9_4kg_nettopreis*1.1, 2))
            berg_9_4kg_info = berg_9_4kg_info.set_index('Art. Nr.:')

            berg_9_1kg_info = self.milchlisten_dict['fulllist'][self.milchlisten_dict['titles'] + ['Art. Nr.:']].loc[self.milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 9') !=-1)]
            berg_9_1kg_info['Produkt'] = 'Bergkäse 9 Mon. 1kg Stück'
            berg_9_1kg_info['Art. Nr.:'] = berg_9_1kg_artnr
            berg_9_1kg_info['Netto'] = str(berg_9_1kg_nettopreis)
            berg_9_1kg_info['Brutto'] = str(round(berg_9_1kg_nettopreis*1.1, 2))
            berg_9_1kg_info = berg_9_1kg_info.set_index('Art. Nr.:')

            # artikelnummer von bergkäse 9 monate korrigieren
            try:
                berg_9_vorrat = vorrat.get_value(berg_9_artnr, 'Vorrat (in kg)')
                vorrat = vorrat.drop(berg_9_artnr)

                berg_9_bestellung = self.milchlisten_dict['sumorders'].loc[berg_9_artnr]
                sumorders = self.milchlisten_dict['sumorders'].drop(berg_9_artnr)

                bestellliste = bestellliste.drop(berg_9_artnr)

                checklisttitles = checklisttitles.drop(berg_9_artnr)
            except Exception:
                pass

            # vorrat und bestellmenge zu bestelltem produkt schreiben (1k bevorzugt)
            if berg_9_1kg > 0 or berg_9_vorrat < 0:
                vorrat.loc[berg_9_1kg_artnr] = berg_9_vorrat
                self.milchlisten_dict['sumorders'].loc[berg_9_1kg_artnr] = berg_9_bestellung
            elif berg_9_4kg > 0:
                vorrat.loc[berg_9_4kg_artnr] = berg_9_vorrat
                sumorders.loc[berg_9_4kg_artnr] = berg_9_bestellung


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
            berg_3_artnr = self.milchlisten_dict['fulllist']['Art. Nr.:'].loc[self.milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 3') !=-1)].get_values()[0].zfill(6)

            berg_3_1kg_artnr = '393004'
            berg_3_1kg_nettopreis = 11.85

            berg_3_4kg_artnr = '393003'
            berg_3_4kg_nettopreis = 11.81

            # separate bergkäsebestellung in 4kg und 1kg stücke
            if bestellliste.get_value(berg_3_artnr, 'Bestellmenge') >= 4:
                berg_3_4kg = bestellliste.get_value(berg_3_artnr, 'Bestellmenge')//4
                berg_3_1kg = bestellliste.get_value(berg_3_artnr, 'Bestellmenge')%4
            else:
                berg_3_4kg = 0.
                berg_3_1kg = bestellliste.get_value(berg_3_artnr, 'Bestellmenge')

            berg_3_4kg_info = self.milchlisten_dict['fulllist'][self.milchlisten_dict['titles'] + ['Art. Nr.:']].loc[self.milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 3') !=-1)]
            berg_3_4kg_info['Produkt'] = 'Bergkäse 3 Mon. 4kg Stück'
            berg_3_4kg_info['Art. Nr.:'] = berg_3_4kg_artnr
            berg_3_4kg_info['Netto'] = str(berg_3_4kg_nettopreis)
            berg_3_4kg_info['Brutto'] = str(round(berg_3_4kg_nettopreis*1.1, 2))
            berg_3_4kg_info = berg_3_4kg_info.set_index('Art. Nr.:')

            berg_3_1kg_info = self.milchlisten_dict['fulllist'][self.milchlisten_dict['titles'] + ['Art. Nr.:']].loc[self.milchlisten_dict['fulllist']['Produkt'].apply(lambda x: str(x).find('Bergkäse 3') !=-1)]
            berg_3_1kg_info['Produkt'] = 'Bergkäse 3 Mon. 1kg Stück'
            berg_3_1kg_info['Art. Nr.:'] = berg_3_1kg_artnr
            berg_3_1kg_info['Netto'] = str(berg_3_1kg_nettopreis)
            berg_3_1kg_info['Brutto'] = str(round(berg_3_1kg_nettopreis*1.1, 2))
            berg_3_1kg_info = berg_3_1kg_info.set_index('Art. Nr.:')

            # artikelnummer für bergkäse 3 monate korrigieren
            try:
                berg_3_vorrat = vorrat.get_value(berg_3_artnr, 'Vorrat (in kg)')
                vorrat = vorrat.drop(berg_3_artnr)

                berg_3_bestellung = self.milchlisten_dict['sumorders'].loc[berg_3_artnr]
                sumorders = self.milchlisten_dict['sumorders'].drop(berg_3_artnr)

                bestellliste = bestellliste.drop(berg_3_artnr)

                checklisttitles = checklisttitles.drop(berg_3_artnr)
            except Exception:
                pass

            # vorrat zu bestelltem produkt schreiben (1k bevorzugt)
            if berg_3_1kg > 0 or berg_3_vorrat < 0:
                vorrat.loc[berg_3_1kg_artnr] = berg_3_vorrat
                self.milchlisten_dict['sumorders'].loc[berg_3_1kg_artnr] = berg_3_bestellung
            elif berg_3_4kg > 0:
                vorrat.loc[berg_3_4kg_artnr] = berg_3_vorrat
                self.milchlisten_dict['sumorders'].loc[berg_3_4kg_artnr] = berg_3_bestellung


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
        n_lists = len(self.milchlisten_dict['names'])//self.max_names + 1

        # milchlisten erstellen
        for i, names_choice in enumerate(np.array_split(self.milchlisten_dict['names'], n_lists)):

            # boolean array für zeilen die bestellungen enthalten
            entries_i = ~np.array(list(map(np.all, self.milchlisten_dict['orders'][names_choice].isnull().values)))

            orders_i = self.milchlisten_dict['orders'][self.milchlisten_dict['titles'] + list(names_choice)]

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
        checklisttitles.rename_axis({'Brutto' : 'Preis'}, axis='columns', inplace=True)

        checkliste = pd.concat([checklisttitles, sumorders, vorrat, bestellliste], axis=1)
        checkliste.index.name = 'Art. Nr.:'



        #checkliste_plot = render_mpl_table(checkliste.fillna(''), font_size=10)
        #checkliste_plot.savefig(os.path.join(currpath, 'checkliste.pdf'))

        # astype(object) wird benötigt damit integer im latex-file nicht als float dargestellt werden (1 statt 1.0)
        self.makelatexfile(checkliste.astype(object),
                      'Checkliste_KW' + str(KW),
                      template='checkliste')


    def gui(self):
        frame = tk.Frame(self.root)

        # Kalenderwochen-variable
        KW_var = tk.StringVar(value='0')
        tk.Label(frame, text = 'Aktuelle Kalenderwoche:   KW').grid(row=0, column=0)
        tk.Entry(frame, textvariable=KW_var).grid(row=0, column=1)

        def open_file_dialog():
            self.returned_values['foldername'] = filedialog.askdirectory()
            _ = read_callback()

        def generate_files():
            if 'foldername' in self.returned_values:
                _ = getresult(['KW'] + self.vorratsliste,
                              [KW_var] + vorrat_vars)

                self.milchlisten_erzeugen()
            else:
                print('select foldername first')

        def getresult(names, variables):
            for name, var in zip(names, variables):
                self.returned_values[name] = var.get()
            return


        # add a button for file-dialog
        tk.Button(self.root, text='Ordner auswählen', command=open_file_dialog).pack()


        # header
        #tk.Label(frame, text = 'Produktname').grid(row=1, column=0)
        tk.Label(frame, text = '').grid(row=1, column=1)
        tk.Label(frame, text = 'Mindestbestellmenge').grid(row=1, column=2)
        tk.Label(frame, text = 'Bestellt').grid(row=1, column=3)
        tk.Label(frame, text = 'Total').grid(row=1, column=4)


        vorrat_vars = [tk.StringVar(value='0') for i in self.vorratsliste]
        best_vars = [tk.StringVar(value='--') for i in self.vorratsliste]
        mind_best_vars = [tk.StringVar(value='--') for i in self.vorratsliste]
        tot_best_vars = [tk.StringVar(value='--') for i in self.vorratsliste]
        vorrat_entrys = []
        for i, [name, vorrat_var, best_var, mind_best_var, tot_best_var] in enumerate(zip(self.vorratsliste,
                                                    vorrat_vars,
                                                    best_vars,
                                                    mind_best_vars,
                                                    tot_best_vars)):

            # add a name to each row
            tk.Label(frame, text=name + '   ').grid(row=i + 2, column=0, sticky=tk.W)

            # add an entry-cell to each row
            entry = tk.Entry(frame, textvariable = vorrat_var)
            vorrat_entrys += [entry]
            entry.grid(row=i + 2, column=1)

            # add mindestbestellmenge to each row
            tk.Label(frame, textvariable = mind_best_var
                     ).grid(row=i + 2, column=2, sticky=tk.E)
            # add mindestbestellmenge to each row
            tk.Label(frame, textvariable = best_var
                     ).grid(row=i + 2, column=3, sticky=tk.E)
            # add total bestellmenge to each row
            tk.Label(frame, textvariable = tot_best_var
                     ).grid(row=i + 2, column=4, sticky=tk.E)



        frame.pack()


        def read_callback():
            _ = self.read_list()
            # mindestbestellmengen setzen
            mind_bestellmengen=[self.milchlisten_dict['vorrats_bestellmengen'][i] for i in self.milchlisten_dict['vorrats_index']]
            vorratprod_bestellungen = [self.milchlisten_dict['sumorders'].loc[i].values.flatten()[0] for i in self.milchlisten_dict['vorrats_index']]
            for i, [mind, best] in enumerate(zip(mind_bestellmengen, vorratprod_bestellungen)):
                mind_best_vars[i].set(mind)
            # bestellte menge setzen
                best_vars[i].set(best)
            # bestellmenge - mindestbestellmenge in das entry-feld schreiben
                vorrat_vars[i].set(str(np.round(float(mind) - float(best), 2)))
            # totale bestellung setzen
                tot_best_vars[i].set(str(np.round(float(vorrat_vars[i].get()) + float(best), 2)))


        def add_vorrat(event):
            # totale bestellung setzen
            for i, val in enumerate([self.milchlisten_dict['sumorders'].loc[i].values.flatten()[0] for i in self.milchlisten_dict['vorrats_index']]):
                tot_best_vars[i].set(str(np.round(float(val) + float(vorrat_vars[i].get()), 2)))

        for i in vorrat_entrys:
            i.bind("<Return>", add_vorrat)



        # tk.Button(self.root, text="read list",
        #           command=read_callback).pack()



        # add a button to generate the lists
        tk.Button(self.root, text='Milchlisten erzeugen',
                  command= generate_files).pack()




        self.root.mainloop()

        self.root.quit()

        return self.returned_values


if __name__ is '__main__':
    asdf = milchliste()
    asdf.gui()
    print(asdf)