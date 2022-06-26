import tkinter.filedialog
from tkinter import *
from tkinter.ttk import Treeview
from functools import partial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from re import fullmatch
import openpyxl


import storage
from db import read_query, get_id


class MultipleEntry(Frame):
    """
    Grid of Entry widgets. 1st row - disabled headers.
    """
    def __init__(self, root, hdrs):
        super().__init__(root)
        self.headers = []
        self.entry = []
        self.vcmd = (self.register(self.validate), '%P', '%W')
        self.upd(hdrs)

    def get(self) -> list:
        """
        :return: list of data from 2nd row
        """
        get_all = []
        for i in self.entry:
            get_all.append(i.get())
        return get_all

    def upd(self, hdrs) -> None:
        """
        Change the size and headers
        """
        for i in range(len(hdrs)):
            self.headers.append(Entry(self, width=5))
            self.headers[i].insert(END, hdrs[i])
            self.headers[i].config(state=DISABLED)
            self.headers[i].grid(row=0, column=i)
            self.entry.append(Entry(self, width=5, validate='focusout', validatecommand=self.vcmd))
            self.entry[i].grid(row=1, column=i)

    def validate(self, value: str, widget: str) -> bool:
        if fullmatch(r'\d+(\.\d*)?', value):
            self.nametowidget(widget).config(fg='black')
            return True
        else:
            self.nametowidget(widget).config(fg='red')
            return False


class Table(LabelFrame):
    """
    Create the table with sorting (LMB on heading), filter (RMB on heading)
    and plotting of selected samples ("Plot" button)
    """
    def __init__(self, root, scr_width, scr_height, columns, name: str, tables):
        super().__init__(root, text=name)
        self.columns = columns
        # Create the LabelFrame with the table label
        self.pack(fill='both', expand=1)
        # Create scrollbar for table
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        # Create the table
        self.trv = Treeview(self, height=int(scr_height/25))
        self.trv['columns'] = self.columns
        self.trv.column('#0', width=0)
        for i in self.columns:
            self.trv.column(i, width=int(scr_width / len(columns)) - 2)
        self.trv.pack()
        # Bind events: right click and left click
        self.trv.bind('<Button-1>', self.click)
        self.trv.bind('<Button-3>', self.rclick)
        # Clear button
        clear_button = Button(self, text='Clear all filters', command=self.clear_filter)
        clear_button.pack(side=LEFT)
        # "Plot" Button
        self.plt_btn = Button(self, text='Plot selected samples', command=self.plot)
        self.plt_btn.pack(side=LEFT)
        self.export_btn = Button(self, text='Export table as xlsx', command=self.export)
        self.export_btn.pack(side=LEFT)
        # Variables with current sorting and filter parameters
        self.order = 0
        self.order_by = columns[0]
        self.filters = set('')
        self.tables = tables
        # Add headings
        for i in range(len(columns)):
            self.trv.heading(i, text=columns[i])
        # Configure scrollbar
        self.scrollbar.config(command=self.trv.yview)
        # update table after creation
        self.update()

    def update(self) -> None:
        """
        Update the table from database, using filters and sorting parameters
        """
        if self.filters != set(''):
            f = f'\nWHERE {" OR ".join(self.filters)}'
        else:
            f = ''
        query = f'SELECT {", ".join(self.columns)}\nFROM {self.tables}{f}\n' \
                f'ORDER BY {self.order_by} {"ASC" if self.order == 0 else "DESC"}'
        rows = read_query(query)
        self.trv.delete(*self.trv.get_children())
        for i in rows:
            self.trv.insert('', 'end', values=i)

    def sorting(self, sort_by: int) -> None:
        """
        Sort the table by specified column and reverse the order (ascending/descending)

        :param sort_by: column number
        """
        self.order_by = self.columns[sort_by]
        if self.order == 0:
            self.order = 1
        else:
            self.order = 0
        self.update()

    def click(self, event) -> None:
        """
        LMB click.

        :param event: click event
        """
        if self.trv.identify('region', event.x, event.y) == 'heading':
            column_number = int(self.trv.identify_column(event.x)[1:]) - 1
            self.sorting(column_number)

    def from_to_filtration(self, column: str, from_e: Entry, to_e: Entry) -> None:
        """
        filter all values between 'from' and 'to' values
        :param column: column name
        :param from_e: From Entry
        :param to_e: to Entry
        """
        self.filters.add(f'{column} BETWEEN {from_e.get()} AND {to_e.get()}')
        self.update()

    def filtration(self, column: str, lb: Listbox) -> None:
        """
        filter the table

        :param column: column
        :param lb: listbox with values
        :return: None
        """
        for i in lb.curselection():
            self.filters.add(f'{column} = "{lb.get(i)}"')
        self.update()

    def clear_filter(self) -> None:
        """
        Clear all filters
        """
        self.filters = set('')
        self.update()

    def rclick(self, event) -> None:
        """
        right click
        :param event: right click event
        """
        if self.trv.identify('region', event.x, event.y) == 'heading':
            # Get column number
            column = int(self.trv.identify_column(event.x)[1:]) - 1
            # Create filter window
            filter_window = Toplevel()
            filter_window.title(string='Filtration')
            f_label = Label(filter_window, text=self.columns[column])
            f_label.pack()
            # Create description for indices
            if column > 8:
                description = Label(filter_window, text=storage.info[self.columns[column]], justify=LEFT)
                description.pack()
            # Create from-to block for columns with date or float numbers
            if column > 8 or column == 1 or column == 3:
                from_to_frame = Frame(filter_window)
                from_to_frame.pack()
                from_l = Label(from_to_frame, text='From:')
                from_l.grid(row=0, column=0)
                from_e = Entry(from_to_frame)
                from_e.grid(row=1, column=0)
                to_l = Label(from_to_frame, text='To:')
                to_l.grid(row=2, column=0)
                to_e = Entry(from_to_frame)
                to_e.grid(row=3, column=0)
                ftf = partial(self.from_to_filtration, self.columns[column], from_e, to_e)
                from_to_filter = Button(from_to_frame, text='Filter', command=ftf)
                from_to_filter.grid(row=6, column=0)
            # Create Listbox
            lb_frame = Frame(filter_window)
            lb_frame.pack()
            lb = Listbox(lb_frame, selectmode=MULTIPLE)
            lb.grid(row=0, column=0)
            # Set is used to exclude repeated data, converted to the sorted list
            lb_set = set()
            for child in self.trv.get_children():
                lb_set.add(self.trv.item(child)['values'][column])
            lb_set = sorted(list(lb_set))
            # Insert it into Listbox
            for i in range(len(lb_set)):
                lb.insert(END, lb_set[i])
            f = partial(self.filtration, self.columns[column], lb)
            # Filter button
            filter_button = Button(lb_frame, text='Filter', command=f)
            filter_button.grid(row=8, column=0)
            # Clear button
            clear_button = Button(lb_frame, text='Clear all', command=self.clear_filter)
            clear_button.grid(row=9, column=0)

    def plot(self) -> None:
        """
        Plot selected samples
        """
        # Get selected
        selected = self.trv.selection()
        # Lists for data
        sel_samp = []
        sel_fract = []
        sel_weight = []

        for i in selected:
            sample = self.trv.item(i)['values'][4]
            # Append sample to sel_samp
            sel_samp.append(sample)
            # Get values from database
            res = read_query(f'''
            SELECT fraction, weight
            FROM fractions
            WHERE sample_id = {get_id('sample', sample)}
            ''')
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
        plot_window = Toplevel()
        plot_window.title(f'Compare Plots {sel_samp}')
        plot_window.state('zoomed')
        # Draw cumulative curves
        plot = Curve(plot_window)
        plot.pack()
        plot.upd(sel_fract, sel_weight, sel_samp)

    def export(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sand database"
        ws.append(storage.headers)
        for i in self.trv.get_children():
            col = read_query(
                f'''SELECT weight, fraction
                FROM fractions
                    INNER JOIN samples USING(sample_id)
                WHERE sample = "{self.trv.item(i)['values'][4]}"'''
            )
            ws.append(self.trv.item(i)['values'] + ['weights:'] + [i[0] for i in col] + ['fractions:'] + [i[1] for i in col])
        wb.save(filename=tkinter.filedialog.asksaveasfilename())


class Curve(Frame):
    """
    Plot of cumulative curve
    """
    def __init__(self, root):
        super().__init__(root)
        # Create the frame for the plot
        self.curve = Figure(figsize=(12, 8), dpi=100)
        # Insert the plot into tk frame
        self.curve_canvas = FigureCanvasTkAgg(self.curve, self)
        NavigationToolbar2Tk(self.curve_canvas, self)
        # Configure the plot
        self.axes = self.curve.add_subplot(xscale='linear', yscale='linear', ybound=(0, 100))
        self.axes.set_title('Cumulative curve')
        self.axes.set_xlabel('Particle diameter, φ')
        self.axes.set_ylabel('Cumulative weight %')
        self.curve_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        # Render the plot
        self.curve_canvas.draw()
        self.renderer = self.curve_canvas.renderer
        self.axes.draw(renderer=self.renderer)

    def upd(self, fractions: list, weights: list, labels: list) -> None:
        """
        Update plot

        :param fractions: list of iterables with float numbers
        :param weights: list of iterables with float numbers
        :param labels: List of plot labels
        """
        self.axes.cla()
        for i in range(len(fractions)):
            self.axes.plot(fractions[i], weights[i], label=labels[i])
        self.axes.legend()
        self.axes.set_title('Cumulative curve')
        self.axes.set_xlabel('Particle diameter, φ')
        self.axes.set_ylabel('Cumulative weight %')
        self.curve_canvas.draw()
