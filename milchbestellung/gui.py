from .milchbestellung import milchliste

class gui(milchliste):
    def __init__(self):
        super().__init__() # inherit init from parent class

        # initialize main window
        self.root = tk.Tk()

    #     self.frame = tk.Frame(self.root)
    #     self.fields = [1,2,3]
    #     self.createWidgets(self.frame)
    #     self.frame.pack()


    # def createWidgets(self, frame):
    #     self.add_field(frame)

    #     self.add_lang = tk.Button(frame, text="add language", command=lambda : self.add_field(frame))
    #     self.add_lang.grid(row=len(self.fields), column=2)


    # def add_field(self, frame):
    #     self.fields.append({})

    #     n = len(self.fields) - 1
    #     self.fields[n]['var'] = tk.StringVar()
    #     self.fields[n]['field'] = tk.Entry(frame, textvariable=self.fields[n]['var'])
    #     self.fields[n]['field'].grid(row=n, column=1)

    #     tk.Label(frame, text=str(n) + "add language").grid(row=n, column=0, sticky=tk.W)


    def gui(self, additional_vorrat_products=[]):
        # reset returned values
        self.returned_values = {}

        #self._set_additional_vorrat_products(additional_vorrat_products)
        self.additional_vorrat_indexes = additional_vorrat_products

        def open_file_dialog():
            self.returned_values['foldername'] = filedialog.askdirectory()
            _ = read_callback()


        def getresult(names, variables):
            for name, var in zip(names, variables):
                self.returned_values[name] = var.get()
            return

        frame_0 = tk.Frame(self.root)
        # add a button for file-dialog
        tk.Button(frame_0, text='Ordner auswählen', command=open_file_dialog).grid(row=0, column=0, padx=20)

        warn_variable = tk.StringVar()
        warn_variable.set('')
        warnlabel = tk.Label(frame_0, textvariable=warn_variable)
        warnlabel.grid(row=0, column=2, padx=20)

        # # Additional vorrat products - variable
        # # initialize frame for additional products
        # frame_add = tk.Frame(self.root)
        # add_vorr_prod_var = tk.StringVar(value='')
        # tk.Label(frame_add, text = 'Zusätzliche vorrats-produkte (komma-getrennt!):').grid(row=0, column=0)
        # add_entry = tk.Entry(frame_add, textvariable=add_vorr_prod_var)
        # #add_entry.bind("<Return>", self.add_field)
        # add_entry.grid(row=0, column=1)
        # frame_add.pack()



        # initialize frame
        frame = tk.Frame(self.root)

        # Kalenderwochen-variable
        KW_var = tk.StringVar(value='0')
        tk.Label(frame, text = 'Aktuelle Kalenderwoche:   KW').grid(row=0, column=0 ,sticky='E')
        tk.Entry(frame, textvariable=KW_var).grid(row=0, column=1)



        # header
        #tk.Label(frame, text = 'Produktname').grid(row=1, column=0)
        #tk.Label(frame, text = 'asdf').grid(row=1, column=1)
        tk.Label(frame, text = 'Mindestbestellmenge').grid(row=1, column=2)
        tk.Label(frame, text = 'Bestellt').grid(row=1, column=3)
        tk.Label(frame, text = 'Total').grid(row=1, column=4)

        nvorrat = len(self.vorratsliste + self.additional_vorrat_indexes)

        vorrat_vars = [tk.StringVar(value='0') for i in range(nvorrat)]
        best_vars = [tk.StringVar(value='--') for i in range(nvorrat)]
        mind_best_vars = [tk.StringVar(value='--') for i in range(nvorrat)]
        tot_best_vars = [tk.StringVar(value='--') for i in range(nvorrat)]

        vorrat_labels = [tk.StringVar(value=name) for name in self.vorratsliste + self.additional_vorrat_indexes]

        tot_best_menge_labels = []
        vorrat_entrys = []
        for i, [name, vorrat_var, best_var, mind_best_var, tot_best_var, vorrat_label] in enumerate(zip(self.vorratsliste + self.additional_vorrat_indexes,
                                                    vorrat_vars,
                                                    best_vars,
                                                    mind_best_vars,
                                                    tot_best_vars,
                                                    vorrat_labels)):

            # add a name to each row
            tk.Label(frame, textvariable=vorrat_label).grid(row=i + 2, column=0, sticky=tk.W)

            # add an entry-cell to each row
            entry = tk.Entry(frame, textvariable = vorrat_var)
            vorrat_entrys += [entry]
            entry.grid(row=i + 2, column=1, padx=20)

            # add mindestbestellmenge to each row
            tk.Label(frame, textvariable = mind_best_var
                     ).grid(row=i + 2, column=2, sticky=tk.E, padx=20)
            # add mindestbestellmenge to each row
            tk.Label(frame, textvariable = best_var
                     ).grid(row=i + 2, column=3, sticky=tk.E, padx=20)
            # add total bestellmenge to each row
            _totlabel = tk.Label(frame, textvariable = tot_best_var)
            tot_best_menge_labels += [_totlabel]
            _totlabel.grid(row=i + 2, column=4, sticky=tk.E, padx=20)

        frame.pack(fill='x')


        def read_callback():
            _ = self.read_list()
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
                mind_best_vars[i].set(mind)

                # bestellte menge setzen
                best_vars[i].set(best)

                # bestellmenge - mindestbestellmenge in das entry-feld schreiben
                if float(best) == 0.:
                    vorrat_vars[i].set(0.)
                elif float(best) > float(mind):
                    vorrat_vars[i].set(str(float(mind)*np.ceil(float(best)/float(mind)) - float(best)))
                elif float(best) <= float(mind):
                    vorrat_vars[i].set(str(np.round(float(mind) - float(best), 2)))

                # totale bestellung setzen
                tot_best_vars[i].set(str(np.round(float(vorrat_vars[i].get()) + float(best), 2)))
                tot_best_menge_labels[i].config(bg='green')
            # TODO
            for vorrat_label, add_vorrat_prod in zip(vorrat_labels, self.vorratsliste + self.additional_vorrat_indexes):
                if add_vorrat_prod in self.additional_vorrat_indexes:
                    vorrat_label.set(self.milchlisten_dict['fulllist']['Produkt'][self.milchlisten_dict['fulllist']['Art. Nr.:']==add_vorrat_prod].values[0])


        def add_vorrat(event):
            if 'foldername' not in self.returned_values:
                warn_variable.set('Zuerst Ordner auswählen!')
                warnlabel.config(bg='red')
            else:
                mind_bestellmengen=[self.milchlisten_dict['vorrats_bestellmengen'][i] for i in self.milchlisten_dict['vorrats_index']]
                # totale bestellung setzen
                for i, val in enumerate([self.milchlisten_dict['sumorders'].loc[i].values.flatten()[0] for i in self.milchlisten_dict['vorrats_index']]):
                    tot_best_vars[i].set(str(np.round(float(val) + float(vorrat_vars[i].get()), 2)))
                    if np.round(float(val) + float(vorrat_vars[i].get()), 2) % mind_bestellmengen[i] == 0:
                        tot_best_menge_labels[i].config(bg="green")
                    else:
                        tot_best_menge_labels[i].config(bg="red")


        for i in vorrat_entrys:
            i.bind("<Return>", add_vorrat)


        def generate_files():
            # check if folder has been selected
            if 'foldername' not in self.returned_values:
                warn_variable.set('Zuerst Ordner auswählen!')
                warnlabel.config(bg='red')

            else:
                # check if all orders are correct
                bestellmengen_OK = True
                mind_bestellmengen=[self.milchlisten_dict['vorrats_bestellmengen'][i] for i in self.milchlisten_dict['vorrats_index']]
                for i, val in enumerate([self.milchlisten_dict['sumorders'].loc[i].values.flatten()[0] for i in self.milchlisten_dict['vorrats_index']]):
                    if np.round(float(val) + float(vorrat_vars[i].get()), 2) % mind_bestellmengen[i] != 0:
                        bestellmengen_OK = False

                if bestellmengen_OK is False:
                    warn_variable.set('Bestellmengen passen nicht zu Mindestbestellmengen!')
                    warnlabel.config(bg='red')
                else:
                    warn_variable.set('Milchlisten werden erzeugt...')
                    warnlabel.config(bg='green')
                    self.root.update_idletasks()
                    _ = getresult(['KW'] + self.vorratsliste + self.additional_vorrat_indexes,
                                  [KW_var] + vorrat_vars)

                    self.milchlisten_erzeugen()

        # add a button to generate the lists
        tk.Button(frame_0, text='Milchlisten erzeugen',
                  command=generate_files).grid(row=0, column=1)
        frame_0.pack(fill='both', padx=10, pady=10)




        self.root.mainloop()

        self.root.quit()

        return self.returned_values
