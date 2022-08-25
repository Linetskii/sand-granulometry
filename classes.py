import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from re import fullmatch
import openpyxl
from contextlib import contextmanager


class MultipleEntry:
    """Grid of Entry widgets. 1st row - disabled headers."""
    frame = None

    def __init__(self, root, hdrs):
        self.frame = tk.Frame(root)
        self.__headers = []
        self.__entry = []
        self.__vcmd = (self.frame.register(self.__validate), '%P', '%W')
        self.upd(hdrs)

    def __len__(self):
        return len(self.__headers)

    def get(self) -> list:
        """:return: list of data from 2nd row"""
        get_all = []
        for i in self.__entry:
            get_all.append(i.get())
        return get_all

    def upd(self, hdrs) -> None:
        """Change the size and headers"""
        for i in range(len(hdrs)):
            self.__headers.append(tk.Entry(self.frame, width=5))
            self.__headers[i].insert(tk.END, hdrs[i])
            self.__headers[i].config(state=tk.DISABLED)
            self.__headers[i].grid(row=0, column=i)
            self.__entry.append(tk.Entry(self.frame, width=5, validate='focusout', validatecommand=self.__vcmd))
            self.__entry[i].grid(row=1, column=i)

    def __validate(self, value: str, widget: str) -> bool:
        """
        Validation of fractions.

        :return: True if the decimal is in the entry, else false. Turn font color to red if not decimal, else black.
        """
        if fullmatch(r'\d+(\.\d*)?', value):
            self.frame.nametowidget(widget).config(fg='black')
            return True
        else:
            self.frame.nametowidget(widget).config(fg='red')
            return False


class Table:
    """
    Create the table with sorting (LMB on heading), filter (RMB on heading),
    plotting of selected samples ("Plot" button) and export ("Export" button)
    """
    frame = None

    def __init__(self, root, db, columns):
        self.__db = db
        self.frame = ttk.Frame(root)
        self.frame.pack(fill='both', expand=1)
        self.__columns = columns
        # Create scrollbar for table
        self.__scrollbar = tk.Scrollbar(self.frame)
        self.__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Create the table
        self.__trv = ttk.Treeview(self.frame)
        self.__trv['columns'] = self.__columns
        self.__trv.column('#0', width=0)
        for i in self.__columns:
            self.__trv.column(i, width=int(self.frame.winfo_screenwidth() / len(columns)) - 2, minwidth=40)
        self.__trv.pack(fill='both', expand=1)
        # Bind events: right click and left click
        self.__trv.bind('<Button-1>', self.__l_click_header)
        self.__trv.bind('<Button-3>', self.__rclick)
        # Clear button
        self.__clear_button = tk.Button(self.frame, text='Clear all filters', command=self.clear_filter)
        self.__clear_button.pack(side=tk.LEFT)
        # "Plot" Button
        self.__plt_btn = tk.Button(self.frame, text='Plot selected samples', command=self.__plot)
        self.__plt_btn.pack(side=tk.LEFT)
        # "Export" button
        self.__export_btn = tk.Button(self.frame, text='Export table as xlsx', command=self.__export)
        self.__export_btn.pack(side=tk.LEFT)
        # "Delete" button
        self.__delete_btn = tk.Button(self.frame, text='Delete selected', command=self.__delete_selected)
        self.__delete_btn.pack(side=tk.LEFT)
        # Variables with current sorting and filter parameters
        self.__order = 0
        self.__order_by = columns[0]
        self.filters = set('')
        self.range_filters = set('')
        self.__tables = '''
            locations
                INNER JOIN samples USING (location_id)
                INNER JOIN zones USING (zone_id)
                INNER JOIN (SELECT person_id as pid, person as collector_name FROM persons) ON pid = samples.collector
                INNER JOIN (SELECT person_id as p, person as performer_name FROM persons) ON p = samples.performer
            '''
        # Add headings
        for i in range(len(columns)):
            self.__trv.heading(i, text=columns[i])
        # Configure scrollbar
        self.__scrollbar.config(command=self.__trv.yview)
        self.__trv['yscrollcommand'] = self.__scrollbar.set
        # Update table after creation
        self.upd()

    @property
    def trv(self):
        return self.__trv

    @trv.setter
    def trv(self, rows):
        for i in rows:
            self.__trv.insert('', 'end', values=i)

    def __create_where_clause(self):
        ranges = " AND ".join(self.range_filters)
        values = " OR ".join(self.filters)
        if self.range_filters == self.filters:
            return ''
        if self.filters == set(''):
            return f'WHERE {ranges}'
        elif self.range_filters == set(''):
            return f'WHERE {values}'
        else:
            return f'\nWHERE {ranges} AND ({values})'

    def upd(self) -> None:
        """Update the table from database, using filters and sorting parameters"""
        columns = ('Collector_name', 'Sampling_date', 'Performer_name', 'Analysis_date', 'Sample', 'Location', 'Zone',
                   'Latitude', 'Longitude', 'Mdφ', 'Mz', 'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')
        query = f'SELECT {", ".join(columns)}\nFROM {self.__tables}{self.__create_where_clause()}\n' \
                f'ORDER BY {self.__order_by} {"ASC" if self.__order == 0 else "DESC"}'
        self.__trv.delete(*self.__trv.get_children())
        self.trv = self.__db.run_query(query)

    def __l_click_header(self, event) -> None:
        """
        LMB click.

        :param event: click event
        """
        if self.__trv.identify('region', event.x, event.y) == 'heading':
            column_number = int(self.__trv.identify_column(event.x)[1:]) - 1
            self.__sorting(column_number)

    def __sorting(self, sort_by: int) -> None:
        """
        Sort the table by specified column and reverse the order (ascending/descending)

        :param sort_by: column number
        """
        self.__order_by = self.__columns[sort_by]
        if self.__order == 0:
            self.__order = 1
        else:
            self.__order = 0
        self.upd()

    def __rclick(self, event) -> None:
        """
        Right click

        :param event: right click event
        """
        if self.__trv.identify('region', event.x, event.y) == 'heading':
            # Get column number
            column = int(self.__trv.identify_column(event.x)[1:]) - 1

            # Create filter window
            if column > 8:
                filter_window = FilterWindowIndex(column, self.__columns[column], self)
            elif column == 1 or column == 3:
                filter_window = FilterWindowRange(column, self.__columns[column], self)
            else:
                filter_window = FilterWindow(column, self.__columns[column], self)

    def clear_filter(self) -> None:
        """Clear all filters"""
        self.filters = set('')
        self.range_filters = set('')
        self.upd()

    # TODO: implement cache
    def __plot(self) -> None:
        """Plot selected samples"""
        # Get selected
        selected = self.__trv.selection()
        # Lists for data
        sel_samp = []
        sel_fract = []
        sel_weight = []
        for i in selected:
            sample = self.__trv.item(i)['values'][4]
            # Append sample to sel_samp
            sel_samp.append(sample)
            # Get values from database
            res = self.__db.run_query(
                f'''
                SELECT fraction, weight
                FROM fractions
                WHERE sample_id = {self.__db.get_id('sample', sample)}
                '''
            )
            fr = []
            w = []
            # Create the lists of fractions and weights for one sample
            for j in res:
                fr.append(j[0])
                w.append(j[1])
            # Append fractions and weights tuples to their lists
            sel_fract.append(tuple(fr))
            sel_weight.append(tuple(w))
        # Create the plot window
        plot_window = tk.Toplevel()
        plot_window.title(f'Compare Plots {sel_samp}')
        plot_window.state('zoomed')
        # Draw cumulative curves
        plot = Curve(plot_window)
        plot.pack()
        plot.upd(sel_fract, sel_weight, sel_samp)

    @staticmethod
    @contextmanager
    def create_workbook():
        wb = openpyxl.Workbook()
        try:
            yield wb
        finally:
            wb.save(filename=f"{tk.filedialog.asksaveasfilename(filetypes=(('Excel file', '*.xlsx'),))}.xlsx")

    def __export(self):
        """Export as Excel .xlsx file"""
        with self.create_workbook() as wb:
            # Active worksheet
            ws = wb.active
            ws.append(self.__db.headers)
            for i in self.__trv.get_children():
                # Read weights and fractions
                col = self.__db.run_query(
                    f'''
                        SELECT weight, fraction
                        FROM fractions
                            INNER JOIN samples USING(sample_id)
                        WHERE sample = "{self.__trv.item(i)['values'][4]}"
                    '''
                )
                # Append row in form: table row + weights + fractions
                ws.append(self.__trv.item(i)['values'] + ['weights:'] + [i[0] for i in col] +
                          ['fractions:'] + [i[1] for i in col])

    def __delete_selected(self):
        selected = self.__trv.selection()
        samples = []
        for i in selected:
            samples.append(self.__trv.item(i)['values'][4])
        if tk.messagebox.askokcancel(title='Delete',
                                     message=f'Please confirm deletion of samples:\n{", ".join(samples)}'):
            self.__db.delete_samples(samples)
            self.upd()


class FilterWindow:
    def __init__(self, column, column_name, table: Table):
        self._filters = table.filters
        self._range_filters = table.range_filters
        self._upd = table.upd
        self._clear_filter = table.clear_filter
        self._column_name = column_name
        # Create filter window
        self._filter_window = tk.Toplevel()
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
    def __init__(self, column, column_name, table: Table):
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

    def __init__(self, column, column_name, table: Table):
        super().__init__(column, column_name, table)
        description = tk.Label(self._filter_window, text=FilterWindowIndex.__info[column_name], justify=tk.LEFT)
        description.pack(side="top")


class Curve(tk.Frame):
    """Plot of cumulative curve"""
    def __init__(self, root):
        super().__init__(root)
        # Create the frame for the plot
        self.__curve = Figure(figsize=(12, 8), dpi=100)
        # Insert the plot into tk frame
        self.__curve_canvas = FigureCanvasTkAgg(self.__curve, self)
        NavigationToolbar2Tk(self.__curve_canvas, self)
        # Configure the plot
        self.__axes = self.__curve.add_subplot(xscale='linear', yscale='linear', ybound=(0, 100))
        self.__axes.set_title('Cumulative curve')
        self.__axes.set_xlabel('Particle diameter, φ')
        self.__axes.set_ylabel('Cumulative weight %')
        self.__curve_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # Render the plot
        self.__curve_canvas.draw()
        self.__renderer = self.__curve_canvas.renderer
        self.__axes.draw(renderer=self.__renderer)

    def upd(self, fractions: list, weights: list, labels: list) -> None:
        """
        Update plot

        :param fractions: list of iterables with float numbers
        :param weights: list of iterables with float numbers
        :param labels: List of plot labels
        """
        self.__axes.cla()
        for i in range(len(fractions)):
            self.__axes.plot(fractions[i], weights[i], label=labels[i])
        self.__axes.legend()
        self.__axes.set_title('Cumulative curve')
        self.__axes.set_xlabel('Particle diameter, φ')
        self.__axes.set_ylabel('Cumulative weight %')
        self.__curve_canvas.draw()
