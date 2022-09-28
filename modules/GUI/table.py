from tkinter import ttk, messagebox
from modules.GUI.plot import Curve
from modules.GUI.filters import *
from modules.backend.excel_export import ExportExcel


class RawTable:
    """
    Create the table with sorting (LMB on heading), filter (RMB on heading),
    plotting of selected samples ("Plot" button) and export ("Export" button)
    """
    frame = None

    def __init__(self, root, db):
        self.__db = db
        self.frame = ttk.Frame(root)
        self.frame.pack(fill='both', expand=1)
        self._columns = db.headers
        # Create scrollbar for table
        self.__scrollbar = tk.Scrollbar(self.frame)
        self.__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.__xscrollbar = tk.Scrollbar(self.frame, orient='horizontal')
        self.__xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        # Create the table
        self.__trv = ttk.Treeview(self.frame)
        self.__trv['columns'] = self._columns
        self.__trv.column('#0', width=0, stretch=False)
        for i in self._columns:
            self.__trv.column(i, width=int(self.frame.winfo_screenwidth() / len(self._columns)) - 2, minwidth=40)
        self.__trv.pack(fill='both', expand=1)
        self.__select_all_btn = tk.Button(self.frame, text='Select_All', command=self.__select_all)
        self.__select_all_btn.pack(side=tk.LEFT)
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
        self._order = 0
        self._order_by = self._columns[1]
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
        for i in range(len(self._columns)):
            self.__trv.heading(i, text=self._columns[i])
        # Configure scrollbar
        self.__scrollbar.config(command=self.__trv.yview)
        self.__trv['yscrollcommand'] = self.__scrollbar.set
        self.__xscrollbar.config(command=self.__trv.xview)
        self.__trv['xscrollcommand'] = self.__xscrollbar.set
        # Update table after creation
        self.upd()

    @property
    def trv(self):
        return self.__trv

    @trv.setter
    def trv(self, rows):
        for i in rows:
            self.__trv.insert('', 'end', values=i)

    def _create_where_clause(self):
        return ''

    def upd(self) -> None:
        """Update the table from database, using filters and sorting parameters"""
        columns = ('Collector_name', 'Sampling_date', 'Performer_name', 'Analysis_date', 'Sample', 'Location', 'Zone',
                   'Latitude', 'Longitude', 'Mdφ', 'Mz', 'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')
        query = f'SELECT {", ".join(columns)}\nFROM {self.__tables}{self._create_where_clause()}\n' \
                f'ORDER BY {self._order_by} {"ASC" if self._order == 0 else "DESC"}'
        self.__trv.delete(*self.__trv.get_children())
        self.trv = self.__db.run_query(query)

    def __select_all(self):
        self.__trv.selection_add(self.__trv.get_children())

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
        plot_window.title(f'Samples: {str(sel_samp)[1:-1]}')
        plot_window.state('zoomed')
        # Draw cumulative curves
        plot = Curve(plot_window)
        plot.upd(sel_fract, sel_weight, sel_samp)

    def __export(self):
        """Export as Excel .xlsx file"""
        ExportExcel(self.__db, self.__trv).export()

    def __delete_selected(self):
        selected = self.__trv.selection()
        samples = []
        for i in selected:
            samples.append(self.__trv.item(i)['values'][4])
        if tk.messagebox.askokcancel(title='Delete',
                                     message=f'Please confirm deletion of samples:\n{", ".join(samples)}'):
            self.__db.delete_samples(samples)
            self.upd()


class SortingTable(RawTable):
    def __init__(self, root, db):
        super().__init__(root, db)
        self.trv.bind('<Button-1>', self.__l_click_header)

    def __l_click_header(self, event) -> None:
        """
        LMB click.

        :param event: click event
        """
        if self.trv.identify('region', event.x, event.y) == 'heading':
            column_number = int(self.trv.identify_column(event.x)[1:]) - 1
            self.__sorting(column_number)

    def __sorting(self, sort_by: int) -> None:
        """
        Sort the table by specified column and reverse the order (ascending/descending)

        :param sort_by: column number
        """
        self._order_by = self._columns[sort_by]
        if self._order == 0:
            self._order = 1
        else:
            self._order = 0
        self.upd()


class Table(SortingTable):
    def __init__(self, root, db):
        super().__init__(root, db)
        self.trv.bind('<Button-3>', self.__rclick)
        # Clear button
        self.__clear_button = tk.Button(self.frame, text='Clear all filters', command=self.clear_filter)
        self.__clear_button.pack(side=tk.LEFT)

    def _create_where_clause(self):
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

    def __rclick(self, event) -> None:
        """
        Right click

        :param event: right click event
        """
        if self.trv.identify('region', event.x, event.y) == 'heading':
            # Get column number
            column = int(self.trv.identify_column(event.x)[1:]) - 1

            # Create filter window
            if column > 8:
                filter_window = FilterWindowIndex(column, self._columns[column], self)
            elif column == 1 or column == 3:
                filter_window = FilterWindowRange(column, self._columns[column], self)
            else:
                filter_window = FilterWindow(column, self._columns[column], self)

    def clear_filter(self) -> None:
        """Clear all filters"""
        self.filters = set('')
        self.range_filters = set('')
        self.upd()
