from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import numpy
from numpy import array, cumsum, interp, log2, around
import re
import openpyxl

import db
import classes
import storage


class App(Tk):
    """
    Main window
    """
    def __init__(self):
        super().__init__()
        # configure the root window
        self.title('Sand granulometric composition')
        self.state('zoomed')
        self.iconphoto(True, PhotoImage(file='icon.png'))
        # create notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        # create tabs
        self.Sample = Sample(self.notebook)
        self.CompareSamples = CompareSamples(self.notebook)
        self.Settings = Settings(self.notebook)
        # self.Help = Help(self.notebook)
        # Add tabs to notebook
        self.notebook.add(self.Sample, text='Add the sample')
        self.notebook.add(self.CompareSamples, text='Compare samples')
        self.notebook.add(self.Settings, text='Settings')
        # self.notebook.add(self.Help, text='Help')


class Sample(ttk.Frame):
    """
    Sample tab
    """
    def __init__(self, container):
        super().__init__(container)
        # Create left frame
        self.left_frame = Frame(self)
        self.left_frame.pack(side=LEFT, anchor='nw', fill='y')
        # Create input block
        self.info_frame = Frame(self.left_frame)
        self.info_frame.pack(anchor='nw')
        # Collector
        self.collector_label = Label(self.info_frame, text='Collector')
        self.collector_label.grid(row=0, column=0, sticky='w')
        self.collector_combobox = ttk.Combobox(self.info_frame, postcommand=self.upd_persons, width=37)
        self.collector_combobox.grid(row=0, column=1)
        # Performer
        self.performer_label = Label(self.info_frame, text='Performer')
        self.performer_label.grid(row=1, column=0, sticky='w')
        self.performer_combobox = ttk.Combobox(self.info_frame, postcommand=self.upd_persons, width=37)
        self.performer_combobox.grid(row=1, column=1)
        # Sample
        self.sample_label = Label(self.info_frame, text='Sample name')
        self.sample_label.grid(row=2, column=0, sticky='w')
        s_vcmd = (self.register(self.validate_sample), '%P')
        self.sample_entry = Entry(self.info_frame, validate='focusout', validatecommand=s_vcmd, width=40)
        self.sample_entry.grid(row=2, column=1)
        # Location
        self.location_label = Label(self.info_frame, text='Location name')
        self.location_label.grid(row=3, column=0, sticky='w')
        self.location_combobox = ttk.Combobox(self.info_frame, postcommand=self.upd_locations, width=37)
        self.location_combobox.grid(row=3, column=1)
        # Zone
        self.zone_label = Label(self.info_frame, text='Zone')
        self.zone_label.grid(row=4, column=0, sticky='w')
        self.zone_combobox = ttk.Combobox(self.info_frame, postcommand=self.upd_zones, width=37)
        self.zone_combobox.grid(row=4, column=1, )
        # Latitude
        self.lat_label = Label(self.info_frame, text='Latitude')
        self.lat_label.grid(row=5, column=0, sticky='w')
        self.lat_entry = Entry(self.info_frame, width=40)
        self.lat_entry.grid(row=5, column=1)
        # Longitude
        self.lon_label = Label(self.info_frame, text='Longitude')
        self.lon_label.grid(row=6, column=0, sticky='w')
        self.lon_entry = Entry(self.info_frame, width=40)
        self.lon_entry.grid(row=6, column=1)
        # Sampling date
        self.date_label = Label(self.info_frame, text='Sampling date')
        self.date_label.grid(row=7, column=0, sticky='w')
        d_vcmd = (self.register(self.vali_date), '%P')
        self.date_entry = Entry(self.info_frame, width=40, validate='focusout', validatecommand=d_vcmd)
        self.date_entry.insert(END, 'yyyy.mm.dd')
        self.date_entry.grid(row=7, column=1)
        # Fractions and weights: Label and table of entry widgets
        self.fractions_label = Label(self.info_frame, text='Fractions and weights:')
        self.fractions_label.grid(row=8, column=0, sticky='w')
        self.weight_entry = classes.MultipleEntry(self.left_frame, upd_fract()[cfg.def_fract])
        self.weight_entry.pack()
        self.bind('<FocusIn>', self.upd_fw)
        # Frame for buttons
        self.btn_frame = Frame(self.left_frame)
        self.btn_frame.pack()
        # "Check" button
        self.upd_btn = Button(self.btn_frame, text='Check', command=self.check_sample)
        self.upd_btn.grid(row=0, column=0)
        # "Add" button
        self.add_btn = Button(self.btn_frame, text='Add', command=self.add_btn_cmd)
        self.add_btn.grid(row=0, column=1)
        # Create indices table
        self.indices_table = ttk.Treeview(self.left_frame, columns=tuple(range(8)), show='headings', height=1)
        self.indices_table['columns'] = list(range(8))
        for i in range(8):
            self.indices_table.column(i, width=50)
            self.indices_table.heading(i, text=storage.headers[9 + i])
        self.indices_table.pack(pady=20)
        # Create fractions table
        self.fractions_table = ttk.Treeview(self.left_frame, columns=('0', '1'), show='headings', height=10)
        self.fractions_table.pack(anchor='n')
        self.fractions_table.heading('0', text='Fractions')
        self.fractions_table.heading('1', text='Weights')
        # Create right frame
        self.right_frame = Frame(self)
        self.right_frame.pack(anchor='nw')
        # Create cumulative curve plot in right frame
        self.curve = classes.Curve(self.right_frame)
        self.curve.pack(padx=20)
        self.import_button = Button(self.left_frame, text='Import Excel file', command=self.import_excel)
        self.import_button.pack()

    def upd_persons(self):
        """
        Update collector and performer combobox values from database
        """
        persons = db.update('person')
        self.collector_combobox['values'] = persons
        self.performer_combobox['values'] = persons

    def upd_zones(self):
        """
        Update zone combobox values from database
        """
        self.zone_combobox['values'] = db.update('zone')

    def upd_locations(self):
        """
        Update location combobox values from database
        """
        self.location_combobox['values'] = db.update('location')

    def upd_fw(self, event) -> None:
        """
        Update fractions entry if scheme was modified in Settings
        """
        if len(self.weight_entry.headers) != len(upd_fract()[cfg.def_fract]):
            self.weight_entry.upd(upd_fract()[cfg.def_fract])

    def gather_info(self) -> storage.SampleData:
        """
        :return: SampleData dataclass with sample information
        """
        return storage.SampleData(
            collector=self.collector_combobox.get(),
            performer=self.performer_combobox.get(),
            sample=self.sample_entry.get(),
            location=self.location_combobox.get(),
            zone=self.zone_combobox.get(),
            lat=self.lat_entry.get(),
            lon=self.lon_entry.get(),
            sampling_date=self.date_entry.get()
        )

    @staticmethod
    def calculate_indices(fractions: numpy.array, weights: numpy.array):
        """
        Calculations for compute and import methods

        :return: Cumulative weights array and IndicesData dataclass with indices
        """
        cumulative_weights = cumsum(100 * weights / sum(weights)).round(cfg.rnd_frac)
        percentiles = (5, 16, 25, 50, 68, 75, 84, 95)
        phi = dict(zip(percentiles, interp(percentiles, cumulative_weights, fractions)))
        return cumulative_weights, storage.IndicesData(
            MdPhi=round(phi[50], cfg.rnd_ind),
            Mz=round((phi[16] + phi[50] + phi[84]) / 3, cfg.rnd_ind),
            QDPhi=round((phi[75] - phi[25]) / 2, cfg.rnd_ind),
            sigma_1=round((phi[84] - phi[16]) / 4 + (phi[95] - phi[5]) / 6.6, cfg.rnd_ind),
            SkqPhi=round((phi[25] + phi[75] - phi[50]) / 2, cfg.rnd_ind),
            Sk_1=round((phi[16] + phi[84] - 2 * phi[50]) / (2 * (phi[84] - phi[16])) +
                       (phi[5] + phi[95] - 2 * phi[50]) / (2 * (phi[95] - phi[5])), cfg.rnd_ind),
            KG=round((phi[95] - phi[5]) / (2.44 * (phi[75] - phi[25])), cfg.rnd_ind),
            SD=round(phi[68], cfg.rnd_ind)
        )

    def compute(self):
        """
        :return: fractions and cumulative weights, indices values in IndicesData dataclass
        """
        fractions = upd_fract()[cfg.def_fract]
        weights = array(self.weight_entry.get(), dtype=float)
        cumulative_weights, indices = self.calculate_indices(fractions, weights)
        return fractions, cumulative_weights, indices

    def check_sample(self) -> None:
        """
        Insert calculated data in tables and plot

        :return: None
        """
        fractions, cumulative_weights, ind = self.compute()
        # Update indices table
        self.indices_table.delete(*self.indices_table.get_children())
        self.indices_table.insert('', 'end', values=ind.get())
        # Update fractions and cumulative weights table
        self.fractions_table.delete(*self.fractions_table.get_children())
        for i in range(len(fractions)):
            self.fractions_table.insert('', 'end', values=(fractions[i], cumulative_weights[i]))
        # Update plot
        self.curve.upd([fractions], [cumulative_weights], [self.sample_entry.get()])

    def add_btn_cmd(self) -> None:
        """
        Add info and calculated parameters into database
        """
        db.add(*self.compute(), self.gather_info())

    def vali_date(self, value: str) -> bool:
        """
        Validation of date

        :param value: date_entry string
        :return: True if value is yyyy.mm.dd date, else False
        """
        pattern = r'[1|2][0-9]{3}\.(0[1-9]|1[0-2])\.(0[1-9]|[1-2][0-9]|3[0-1])'
        if re.fullmatch(pattern, value) is None:
            self.date_entry.config(fg='red')
            self.add_btn.config(state='disabled', text='Please use yyyy.mm.dd date format.')
            return False
        else:
            self.date_entry.config(fg='black')
            self.add_btn.config(state='normal', text='Add')
            return True

    def validate_sample(self, value: str) -> bool:
        """
        Validation of sample
        :param value: sample_entry string
        :return: False if sample name already exists in database
        """
        if value in db.update('sample'):
            self.sample_entry.config(fg='red')
            self.add_btn.config(state='disabled', text=f'Sample "{value}" already exists')
            return False
        else:
            self.date_entry.config(fg='black')
            self.add_btn.config(state='normal', text='Add')
            return True

    def import_excel(self):
        # open Excel workbook
        wb = openpyxl.load_workbook(filedialog.askopenfilename())
        # open active sheet
        worksheet = wb.active
        fractions = []
        # Read fractions
        for col in worksheet.iter_cols(9, worksheet.max_column):
            fractions.append(col[0].value)
        fractions = array(fractions, dtype=float)
        # Read rows
        for i in range(1, worksheet.max_row):
            row = []
            # Read each column in row, write to row
            for col in worksheet.iter_cols(1, worksheet.max_column):
                row.append(col[i].value)
            # Write weights
            weights = array(row[8:worksheet.max_column], dtype=float)
            # Write sample information to SampleData dataclass
            info = storage.SampleData(*row[0:7], row[7].strftime("%Y.%m.%d"))
            # Calculate cumulative weights and indices
            cumulative_weights, indices = self.calculate_indices(fractions, weights)
            db.add(fractions, cumulative_weights, indices, info)


class CompareSamples(ttk.Frame):
    """
    Compare Samoles tab
    """
    def __init__(self, container):
        super().__init__(container)
        # Table
        self.comp_table = classes.Table(self, columns=storage.headers, scr_width=self.winfo_screenwidth(),
                                        scr_height=self.winfo_screenheight(), name='CompareSamples', tables=db.tables)
        self.comp_table.pack()
        # Update Table, when focused
        self.bind('<FocusIn>', self.comp_table.update())


class Settings(ttk.Frame):
    """
    Settings tab
    """
    def __init__(self, container):
        super().__init__(container)
        # Little frame to align blocks
        self.main = Frame(self)
        self.main.pack()
        # General settings LabelFrame
        self.set_lb = LabelFrame(self.main, text='General settings')
        self.set_lb.pack(fill='both')
        # Indices rounding
        self.ind_rnd_label = Label(self.set_lb, text='Indices rounding')
        self.ind_rnd_label.grid(row=0, column=0)
        self.ind_rnd = ttk.Combobox(self.set_lb, values=('1', '2', '3', '4'), width=38)
        self.ind_rnd.insert(END, str(cfg.rnd_ind))
        self.ind_rnd.grid(row=0, column=1)
        # Weights rounding
        self.frac_rnd_label = Label(self.set_lb, text='Weights rounding')
        self.frac_rnd_label.grid(row=1, column=0)
        self.frac_rnd = ttk.Combobox(self.set_lb, values=('1', '2', '3', '4'), width=38)
        self.frac_rnd.insert(END, str(cfg.rnd_frac))
        self.frac_rnd.grid(row=1, column=1)
        # Separator. Currently, used only in next two blocks.
        self.sep_label = Label(self.set_lb, text='Separator')
        self.sep_label.grid(row=3, column=0)
        self.sep_entry = ttk.Combobox(self.set_lb, values=(' ', ', '), width=38)
        self.sep_entry.insert(END, cfg.sep)
        self.sep_entry.grid(row=3, column=1)
        # Fractions scheme selection
        self.fract_label = Label(self.set_lb, text='Select fractions scheme')
        self.fract_label.grid(row=4, column=0)
        self.fract_cb = ttk.Combobox(self.set_lb, postcommand=self.upd_fractions, width=38)
        self.fract_cb.insert(END, cfg.def_fract)
        self.fract_cb.grid(row=4, column=1)
        # Apply Button
        self.apply_button = Button(self.set_lb, text='Apply settings', command=self.apply)
        self.apply_button.grid(row=5, column=0)
        # Converter
        self.conv = LabelFrame(self.main, text='Converter')
        self.conv.pack(fill='both')
        # Input and output
        self.inp_label = Label(self.conv, text='Input')
        self.inp_label.grid(row=0, column=0)
        self.inp = Entry(self.conv, width=48)
        self.inp.grid(row=0, column=1)
        self.outp_label = Label(self.conv, text='Output')
        self.outp_label.grid(row=1, column=0)
        self.outp = Entry(self.conv, width=48)
        self.outp.grid(row=1, column=1)
        # Convert mode
        self.convert_options = ['D(mm) to D(φ)', 'D(mm) to D(μ)', 'D(φ) to D(mm)', 'D(φ) to D(μ)', 'D(μ) to D(mm)',
                                'D(μ) to D(φ)']
        self.convert_combobox = ttk.Combobox(self.conv, values=self.convert_options)
        self.convert_combobox.grid(row=3, column=1)
        # "Convert" button
        self.convert_button = Button(self.conv, text='Convert', command=self.convert)
        self.convert_button.grid(row=3, column=0)
        # Add fractions
        self.fract_lf = LabelFrame(self.main, text='Add fractions scheme')
        self.fract_lf.pack(fill='both')
        # Name
        self.fract_name_label = Label(self.fract_lf, text='Name:')
        self.fract_name_label.grid(row=0, column=0)
        self.fract_name = Entry(self.fract_lf, width=49)
        self.fract_name.grid(row=0, column=1)
        # Scheme
        self.fract_sch_label = Label(self.fract_lf, text='Scheme:')
        self.fract_sch_label.grid(row=1, column=0)
        self.fract_sch = Entry(self.fract_lf, width=49)
        self.fract_sch.grid(row=1, column=1)
        # Add button
        self.fract_add_button = Button(self.fract_lf, text='Add', command=self.add_fractoins)
        self.fract_add_button.grid(row=2, column=0)

    def convert(self) -> None:
        """
        Converter function. Insert into output converted values.
        """
        inp = array(self.inp.get().split(cfg.sep), dtype=float)
        if self.convert_combobox.get() == 'D(mm) to D(φ)':  # -log2(x, mm)
            self.outp.delete(0, END)
            self.outp.insert(END, f'{cfg.sep}'.join(map(str, around(-log2(inp), 2))))
        if self.convert_combobox.get() == 'D(mm) to D(μ)':  # x,mm * 1000 / 2
            self.outp.delete(0, END)
            self.outp.insert(END, f'{cfg.sep}'.join(map(str, inp * 1000)))
        if self.convert_combobox.get() == 'D(φ) to D(mm)':  # 1 / (2^x,phi)
            self.outp.delete(0, END)
            self.outp.insert(END, f'{cfg.sep}'.join(map(str, around(1 / (2 ** inp), 2))))
        if self.convert_combobox.get() == 'D(φ) to D(μ)':  # 1000 / 2^x,phi
            self.outp.delete(0, END)
            self.outp.insert(END, f'{cfg.sep}'.join(map(str, around(1000 / (2 ** inp), 2))))
        if self.convert_combobox.get() == 'D(μ) to D(φ)':  # -log2(x,mu / 1000)
            self.outp.delete(0, END)
            self.outp.insert(END, f'{cfg.sep}'.join(map(str, around(-log2(0.001 * inp), 2))))
        if self.convert_combobox.get() == 'D(μ) to D(mm)':  # x,mu / 1000
            self.outp.delete(0, END)
            self.outp.insert(END, f'{cfg.sep}'.join(map(str, around(0.001 * inp, 2))))

    def apply(self) -> None:
        """
        Apply settings: write it to the config.txt, update cfg
        """
        cfg.sep = self.sep_entry.get()
        cfg.rnd_ind = int(self.ind_rnd.get())
        cfg.rnd_frac = int(self.frac_rnd.get())
        cfg.def_fract = self.fract_cb.get()
        cfg.apply_settings()

    def upd_fractions(self):
        """
        Update fractions combobox
        """
        self.fract_cb['values'] = list(i for i in upd_fract().keys())

    def add_fractoins(self) -> None:
        """
        Add fractions to the fractions.txt, update dictionary
        """
        with open('fractions.txt', 'a') as f:
            f.write(f'\n{self.fract_name.get()}: {self.fract_sch.get()}')
        # upd_fract()


# class Help(ttk.Frame):
#     def __init__(self, container):
#         super().__init__(container)
#         lf_general = LabelFrame(self, text='General information')
#         lf_sample = LabelFrame(self, text='Sample tab')
#         lf_db = LabelFrame(self, text='Database tab')
#         lf_ref = LabelFrame(self, text='References')


def upd_fract() -> dict:
    """
    Read fractions.txt

    :return: dictionary of fractions schemes
    """
    schemes = {}
    with open('fractions.txt', 'r') as f:
        for line in f:
            key, value = line.split(': ')
            value = array(value.split(), dtype=float)
            schemes[key] = value
        return schemes


if __name__ == '__main__':
    # Create database, if not exists
    db.create_db()
    # Create config.txt dataclass
    cfg = storage.CFG()
    # Update config.txt dataclass from config.txt file
    cfg.update()
    # create Tk main window
    app = App()
    app.mainloop()
