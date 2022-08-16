import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from re import fullmatch
import openpyxl

import storage


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


class Table(tk.LabelFrame):
    """
    Create the table with sorting (LMB on heading), filter (RMB on heading),
    plotting of selected samples ("Plot" button) and export ("Export" button)
    """
    def __init__(self, root, db, scr_width, scr_height, columns, name: str):
        self.db = db
        # Create the LabelFrame with the table label
        super().__init__(root, text=name)
        self.pack(fill='both', expand=1)
        self.__columns = columns
        # Create scrollbar for table
        self.__scrollbar = tk.Scrollbar(self)
        self.__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Create the table
        self.__trv = ttk.Treeview(self, height=int(scr_height/25))
        self.__trv['columns'] = self.__columns
        self.__trv.column('#0', width=0)
        for i in self.__columns:
            self.__trv.column(i, width=int(scr_width / len(columns)) - 2)
        self.__trv.pack()
        # Bind events: right click and left click
        self.__trv.bind('<Button-1>', self.__l_click_header)
        self.__trv.bind('<Button-3>', self.__rclick)
        # Clear button
        self.__clear_button = tk.Button(self, text='Clear all filters', command=self.__clear_filter)
        self.__clear_button.pack(side=tk.LEFT)
        # "Plot" Button
        self.__plt_btn = tk.Button(self, text='Plot selected samples', command=self.__plot)
        self.__plt_btn.pack(side=tk.LEFT)
        # "Export" button
        self.__export_btn = tk.Button(self, text='Export table as xlsx', command=self.__export)
        self.__export_btn.pack(side=tk.LEFT)
        # "Delete" button
        self.__delete_btn = tk.Button(self, text='Delete selected', command=self.__delete_selected)
        self.__delete_btn.pack(side=tk.LEFT)
        # Variables with current sorting and filter parameters
        self.__order = 0
        self.__order_by = columns[0]
        self.__filters = set('')
        self.__range_filters = set('')
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
        # Update table after creation
        self.__upd()

    def __upd(self) -> None:
        """Update the table from database, using filters and sorting parameters"""
        columns = ('Collector_name', 'Sampling_date', 'Performer_name', 'Analysis_date', 'Sample', 'Location', 'Zone',
                   'Latitude', 'Longitude', 'Mdφ', 'Mz', 'QDφ', 'σ_1', 'Skqφ', 'Sk_1', 'KG', 'SD')
        ranges = " AND ".join(self.__range_filters)
        values = " OR ".join(self.__filters)
        if self.__range_filters != self.__filters:
            if self.__filters == set(''):
                f = f'WHERE {ranges}'
            elif self.__range_filters == set(''):
                f = f'WHERE {values}'
            else:
                f = f'\nWHERE {ranges} AND ({values})'
        else:
            f = ''

        query = f'SELECT {", ".join(columns)}\nFROM {self.__tables}{f}\n' \
                f'ORDER BY {self.__order_by} {"ASC" if self.__order == 0 else "DESC"}'
        rows = self.db.run_query(query)
        self.__trv.delete(*self.__trv.get_children())
        for i in rows:
            self.__trv.insert('', 'end', values=i)

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
        self.__upd()

    def __rclick(self, event) -> None:
        """
        Right click

        :param event: right click event
        """
        if self.__trv.identify('region', event.x, event.y) == 'heading':
            # Get column number
            column = int(self.__trv.identify_column(event.x)[1:]) - 1
            # Create filter window
            filter_window = tk.Toplevel()
            filter_window.title(string='Filtration')
            f_label = tk.Label(filter_window, text=self.__columns[column])
            f_label.pack()
            # Create description for indices
            if column > 8:
                description = tk.Label(filter_window, text=storage.info[self.__columns[column]], justify=tk.LEFT)
                description.pack()
            # Create from-to block for columns with date or float numbers
            if column > 8 or column == 1 or column == 3:
                from_to_frame = tk.Frame(filter_window)
                from_to_frame.pack()
                from_l = tk.Label(from_to_frame, text='From:')
                from_l.grid(row=0, column=0)
                from_e = tk.Entry(from_to_frame, width=32)
                from_e.grid(row=1, column=0)
                to_l = tk.Label(from_to_frame, text='To:')
                to_l.grid(row=2, column=0)
                to_e = tk.Entry(from_to_frame, width=32)
                to_e.grid(row=3, column=0)
                ftf = partial(self.__from_to_filtration, self.__columns[column], from_e, to_e)
                from_to_filter = tk.Button(from_to_frame, text='Filter', command=ftf)
                from_to_filter.grid(row=6, column=0)
            # Create Listbox
            lb_frame = tk.Frame(filter_window)
            lb_frame.pack()
            lb = tk.Listbox(lb_frame, selectmode=tk.MULTIPLE, width=32)
            lb.grid(row=0, column=0)
            # Set is used to exclude repeated data, converted to the sorted list
            lb_set = set()
            for child in self.__trv.get_children():
                lb_set.add(self.__trv.item(child)['values'][column])
            lb_set = sorted(list(lb_set))
            # Insert it into Listbox
            for i in range(len(lb_set)):
                lb.insert(tk.END, lb_set[i])
            f = partial(self.__filtration, self.__columns[column], lb)
            # Filter button
            filter_button = tk.Button(lb_frame, text='Filter', command=f)
            filter_button.grid(row=8, column=0)
            # Clear button
            clear_button = tk.Button(lb_frame, text='Clear all', command=self.__clear_filter)
            clear_button.grid(row=9, column=0)

    def __from_to_filtration(self, column: str, from_e: tk.Entry, to_e: tk.Entry) -> None:
        """
        Leave values between 'from' and 'to'

        :param column: column name
        :param from_e: From Entry
        :param to_e: to Entry
        """
        self.__range_filters.add(f'{column} BETWEEN "{from_e.get()}" AND "{to_e.get()}"')
        self.__upd()

    def __filtration(self, column: str, lb: tk.Listbox) -> None:
        """
        Filter the table

        :param column: column
        :param lb: listbox with values
        :return: None
        """
        for i in lb.curselection():
            self.__filters.add(f'{column} = "{lb.get(i)}"')
        self.__upd()

    def __clear_filter(self) -> None:
        """Clear all filters"""
        self.__filters = set('')
        self.__range_filters = set('')
        self.__upd()

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
            res = self.db.run_query(
                f'''
                SELECT fraction, weight
                FROM fractions
                WHERE sample_id = {self.db.get_id('sample', sample)}
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

    def __export(self):
        """Export as Excel .xlsx file"""
        # Create workbook and worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sand database"
        ws.append(self.db.headers)  # Append headers
        # For each row...
        for i in self.__trv.get_children():
            # Read weights and fractions
            col = self.db.run_query(
                f'''
                    SELECT weight, fraction
                    FROM fractions
                        INNER JOIN samples USING(sample_id)
                    WHERE sample = "{self.__trv.item(i)['values'][4]}"
                '''
            )
            # Append row in for: table row + weights + fractions
            ws.append(self.__trv.item(i)['values'] + ['weights:'] + [i[0] for i in col] +
                      ['fractions:'] + [i[1] for i in col])
        wb.save(filename=f"{tk.filedialog.asksaveasfilename(filetypes=(('Excel file', '*.xlsx'),))}.xlsx")  # Save book

    def __delete_selected(self):
        selected = self.__trv.selection()
        samples = []
        for i in selected:
            samples.append(self.__trv.item(i)['values'][4])
        if tk.messagebox.askokcancel(title='Delete',
                                     message=f'Please confirm deletion of samples:\n{", ".join(samples)}'):
            self.db.delete_samples(samples)
            self.__upd()


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
