from tkinter import *
from tkinter.ttk import Treeview
from functools import partial
from db import read_query
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# class MultipleEntry:
#     def __init__(self, root, hdrs, width):
#         self.frame = Frame(root)
#         self.headers = []
#         self.entry = []
#         for i in range(len(hdrs)):
#             self.headers.append(Entry(self.frame, width=width))
#             self.headers[i].insert(END, hdrs[i])
#             self.headers[i].config.txt(state=DISABLED)
#             self.headers[i].grid(row=0, column=i)
#             self.entry.append(Entry(self.frame, width=width))
#             self.entry[i].grid(row=1, column=i)
#             self.entry[i].bind('<Right>', self.right)
#
#     def right(self, event):
#         event.


class Table:
    """
    Create the table with sorting (LMB on heading) and filter (RMB on heading)
    """
    def __init__(self, root, scr_width, scr_height, columns, name: str, tables):
        self.columns = columns
        # Create the LabelFrame with the table label
        self.wrapper = LabelFrame(root, text=name)
        self.wrapper.pack(fill='both', expand=1)
        # Create scrollbar for table
        self.scrollbar = Scrollbar(self.wrapper)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        # Create the table
        # self.trv = Treeview(self.wrapper, columns=list(range(self.width)), show='headings', height=rows,
        #                     yscrollcommand=self.scrollbar.set, selectmode='extended')
        self.trv = Treeview(self.wrapper, height=int(scr_height/30))
        self.trv['columns'] = self.columns
        self.trv.column('#0', width=0)
        for i in self.columns:
            self.trv.column(i, width=int(scr_width / len(columns)) - 2)

        # Bind events: right click, left click and hoover
        self.trv.bind('<Button-1>', self.click)
        self.trv.bind('<Button-3>', self.rclick)
        # self.trv.bind('<Motion>', self.hlp)
        self.trv.pack()
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

    # def hlp(self, event):
    #     """
    #     Show the description of each header
    #     :param event: when description shows
    #     :return: None
    #     """
    #     self.trv.unbind('<Motion>')
    #     if self.trv.identify('region', event.x, event.y) == 'heading':
    #         column_number = int(self.trv.identify_column(event.x)[1]) - 1
    #         print(self.columns[column_number])
    #     self.trv.bind('<Motion>', self.hlp)

    def update(self):
        """
        update the table

        :return:
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

    def sorting(self, sort_by):
        """
        Sort the table by specified column and reverse the order (ascending/descending)

        :param sort_by: column number
        :return: None
        """
        self.order_by = self.columns[sort_by]
        if self.order == 0:
            self.order = 1
        else:
            self.order = 0
        self.update()

    def click(self, event):
        """
        LMB click.

        :param event:
        :return:
        """
        if self.trv.identify('region', event.x, event.y) == 'heading':
            column_number = int(self.trv.identify_column(event.x)[1]) - 1
            self.sorting(column_number)

    def filtration(self, column, lb):
        """
        filter the table

        :param column: column
        :param lb: listbox with values
        :return: None
        """
        for i in lb.curselection():
            self.filters.add(f'{column} = "{lb.get(i)}"')
        self.update()

    def clear_filter(self):
        """
        Clear all filters

        :return: None
        """
        self.filters = set('')
        self.update()

    def rclick(self, event):
        """
        right click
        :param event:
        :return: None
        """
        if self.trv.identify('region', event.x, event.y) == 'heading':
            column = int(self.trv.identify_column(event.x)[1]) - 1
            filter_window = Tk()
            filter_window.attributes('-topmost', 1)
            filter_window.title(string='Filter')
            from_l = Label(filter_window, text='From:')
            from_l.grid(row=0, column=0)
            to_l = Label(filter_window, text='To:')
            to_l.grid(row=1, column=0)
            lb = Listbox(filter_window, selectmode=MULTIPLE)
            lb.grid(row=2, column=0)
            # child_set = set()
            # for child in self.trv.get_children():
            #   child_set.add(self.trv.item(child)['values'][column])
            # for i in child_set:
            #   lb.insert(END, i)
            # better write it before
            for child in self.trv.get_children():
                lb.insert(END, self.trv.item(child)['values'][column])
            f = partial(self.filtration, self.columns[column], lb)
            filter_button = Button(filter_window, text='Filter', command=f)
            filter_button.grid(row=3, column=0)
            clear_button = Button(filter_window, text='Clear all', command=self.clear_filter)
            clear_button.grid(row=4, column=0)


class Curve:
    """
    Plot of sand cumulative curve
    """
    def __init__(self, root):
        # Create the frame for the plot
        self.curve_frame = Frame(root, height=1, width=1)
        self.curve = Figure(figsize=(6, 4), dpi=100)
        # Insert the plot into tk frame
        self.curve_canvas = FigureCanvasTkAgg(self.curve, self.curve_frame)
        NavigationToolbar2Tk(self.curve_canvas, self.curve_frame)
        # Configure the plot
        self.axes = self.curve.add_subplot(xscale='linear', yscale='linear', ybound=(0, 100))
        self.axes.plot([], [])
        self.axes.set_title('Cumulative curve')
        self.axes.set_xlabel('Particle diameter, φ')
        self.axes.set_ylabel('Cumulative weight %')
        self.curve_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        # Render the plot
        self.curve_canvas.draw()
        self.renderer = self.curve_canvas.renderer
        self.axes.draw(renderer=self.renderer)

    def update(self, fractions, weights):
        self.axes.cla()
        self.axes.plot(fractions, weights, color='black')
        self.axes.set_title('Cumulative curve')
        self.axes.set_xlabel('Particle diameter, φ')
        self.axes.set_ylabel('Cumulative weight %')
        self.curve_canvas.draw()
