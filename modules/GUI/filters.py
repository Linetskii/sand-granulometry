import tkinter as tk


class FilterWindow:
    def __init__(self, column, column_name, table):
        self._filters = table.filters
        self._range_filters = table.range_filters
        self._upd = table.upd
        self._clear_filter = table.clear_filter
        self._column_name = column_name
        # Create filter window
        self._filter_window = tk.Toplevel()
        self._filter_window.grab_set()
        self._filter_window.title(string="Filtration")
        self._f_label = tk.Label(self._filter_window, text=column_name)
        self._f_label.pack(side="top")
        # Create Listbox
        self._lb_frame = tk.Frame(self._filter_window)
        self._lb_frame.pack(side="bottom")
        self._lb = tk.Listbox(self._lb_frame, selectmode=tk.MULTIPLE, width=32)
        self._lb.grid(row=0, column=0)
        # Set is used to exclude repeated data, converted to the sorted list
        self._lb_set = set()
        for child in table.trv.get_children():
            self._lb_set.add(table.trv.item(child)['values'][column])
        self._lb_set = sorted(list(self._lb_set))
        # Insert it into Listbox
        for i in range(len(self._lb_set)):
            self._lb.insert(tk.END, self._lb_set[i])
        # Filter button
        self.filter_button = tk.Button(self._lb_frame, text='Filter', command=self._filtration)
        self.filter_button.grid(row=8, column=0)
        # Clear button
        self.clear_button = tk.Button(self._lb_frame, text='Clear all', command=self._clear_filter)
        self.clear_button.grid(row=9, column=0)

    def _filtration(self) -> None:
        """
        Update table filters and renew the table

        :return: None
        """
        for i in self._lb.curselection():
            self._filters.add(f'{self._column_name} = "{self._lb.get(i)}"')
        self._upd()


class FilterWindowRange(FilterWindow):
    def __init__(self, column, column_name, table):
        super().__init__(column, column_name, table)
        self._from_to_frame = tk.Frame(self._filter_window)
        self._from_to_frame.pack(side='bottom')
        self._from_l = tk.Label(self._from_to_frame, text="From:")
        self._from_l.grid(row=0, column=0)
        self._from_e = tk.Entry(self._from_to_frame, width=32)
        self._from_e.grid(row=1, column=0)
        self._to_l = tk.Label(self._from_to_frame, text="To:")
        self._to_l.grid(row=2, column=0)
        self._to_e = tk.Entry(self._from_to_frame, width=32)
        self._to_e.grid(row=3, column=0)
        self._from_to_filter = tk.Button(self._from_to_frame, text='Filter', command=self._from_to_filtration)
        self._from_to_filter.grid(row=6, column=0)

    def _from_to_filtration(self) -> None:
        self._range_filters.add(f'{self._column_name} BETWEEN "{self._from_e.get()}" AND "{self._to_e.get()}"')
        self._upd()


class FilterWindowIndex(FilterWindowRange):
    # Sand size classification
    __sand = '\n0 to -1     Very coarse\n1 to 0      Coarse\n' \
             '2 to 1      Medium\n3 to 2      Fine\n4 to 3      Very fine\n'
    # Indices info
    __info = {'Mdφ': 'Median particle diameter\nMdφ = φ50' + __sand,
              'Mz': 'Graphic mean particle diameter (Mz)\nMz = (φ16 + φ50 + φ84) / 3' + __sand,
              'QDφ': 'Phi quartile deviation\nQDφ = (φ75 - φ25) / 2\n',
              'σ_1': 'Inclusive graphic standard deviation\nσi= (φ84 - φ16) / 4 + (φ95 - φ5) / 6.6\n'
              '<0.5    Good sorting\n0.5-1   Moderate sorting\n1<      Poor sorting\n',
              'Skqφ': 'Phi quartile skewness\nSkqφ = (φ25 + φ75 - φ50) / 2\n',
              'Sk_1': 'Inclusive graphic skewness\nSki = (φ16 + φ84 - 2φ50) / (2(φ84 - φ16)) + \n(φ5 + φ95 - 2φ5) / '
                    '(2(φ95 - φ50))\n+0.1< fine skewed sand\n-0.1-+0.1 Near symmetry\n<-0.1 coarse skewed sand\n',
              'KG': 'Kurtosis\nKG = ((φ95 - φ5) / 2.44(φ75 - φ25)\n1.0< wide spread\n<1.0 little spread\n',
              'SD': 'Standard deviation\nSD = φ86\n'
              }

    def __init__(self, column, column_name, table):
        super().__init__(column, column_name, table)
        description = tk.Label(self._filter_window, text=FilterWindowIndex.__info[column_name], justify=tk.LEFT)
        description.pack(side="top")
