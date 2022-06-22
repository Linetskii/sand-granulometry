from tkinter import *
from tkinter import ttk
from numpy import array, cumsum, interp, log2, around
import re

import db
import classes
import storage


class App(Tk):
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
    def __init__(self, container):
        super().__init__(container)
        db.update_pzl()
        self.left_frame = Frame(self)
        self.left_frame.pack(side=LEFT, anchor='nw')
        # Create input block
        self.info_frame = Frame(self.left_frame)
        self.info_frame.pack(anchor='nw')

        self.collector_label = Label(self.info_frame, text='Collector')
        self.collector_label.grid(row=0, column=0, sticky='w')
        self.collector_combobox = ttk.Combobox(self.info_frame, values=db.upd_dict['persons'], width=37)
        self.collector_combobox.grid(row=0, column=1)

        self.performer_label = Label(self.info_frame, text='Performer')
        self.performer_label.grid(row=1, column=0, sticky='w')
        self.performer_combobox = ttk.Combobox(self.info_frame, values=db.upd_dict['persons'], width=37)
        self.performer_combobox.grid(row=1, column=1)

        self.sample_label = Label(self.info_frame, text='Sample name')
        self.sample_label.grid(row=2, column=0, sticky='w')
        self.sample_entry = Entry(self.info_frame, width=40)
        self.sample_entry.grid(row=2, column=1)

        self.location_label = Label(self.info_frame, text='Location name')
        self.location_label.grid(row=3, column=0, sticky='w')
        self.location_combobox = ttk.Combobox(self.info_frame, values=db.upd_dict['locations'], width=37)
        self.location_combobox.grid(row=3, column=1)

        self.zone_label = Label(self.info_frame, text='Zone')
        self.zone_label.grid(row=4, column=0, sticky='w')
        self.zone_combobox = ttk.Combobox(self.info_frame, values=db.upd_dict['zones'], width=37)
        self.zone_combobox.grid(row=4, column=1, )

        self.lat_label = Label(self.info_frame, text='Latitude')
        self.lat_label.grid(row=5, column=0, sticky='w')
        self.lat_entry = Entry(self.info_frame, width=40)
        self.lat_entry.grid(row=5, column=1)

        self.lon_label = Label(self.info_frame, text='Longitude')
        self.lon_label.grid(row=6, column=0, sticky='w')
        self.lon_entry = Entry(self.info_frame, width=40)
        self.lon_entry.grid(row=6, column=1)

        self.date_label = Label(self.info_frame, text='Sampling date')
        self.date_label.grid(row=7, column=0, sticky='w')
        d_vcmd = (self.register(self.vali_date), '%P')
        self.date_entry = Entry(self.info_frame, width=40, validate='focusout', validatecommand=d_vcmd)
        self.date_entry.insert(END, 'yyyy.mm.dd')
        self.date_entry.grid(row=7, column=1)

        self.fractions_label = Label(self.info_frame, text='Fractions')
        self.fractions_label.grid(row=8, column=0, sticky='w')
        self.fractions_combobox = ttk.Combobox(self.info_frame, postcommand=upd_fract,
                                               values=list(db.upd_dict['fractions'].keys()), width=37)
        self.fractions_combobox.grid(row=8, column=1)

        self.weight_label = Label(self.info_frame, text='Weight of fractions')
        self.weight_label.grid(row=9, column=0, sticky='w')
        self.weight_entry = Entry(self.info_frame, width=40)
        self.weight_entry.grid(row=9, column=1)
        # frame for buttons
        self.btn_frame = Frame(self.info_frame)
        self.btn_frame.grid(row=10, column=1)
        # "check" button
        self.upd_btn = Button(self.btn_frame, text='Check', command=self.check_sample)
        self.upd_btn.grid(row=0, column=0)
        # "add" button
        self.add_btn = Button(self.btn_frame, text='Add', command=self.add_btn_cmd)
        self.add_btn.grid(row=0, column=1)

        # self.raw_weight = table.MultipleEntry(self, db.upd_dict['fractions'][cfg.def_fract], width=10)
        # self.raw_weight.frame.pack(side=TOP, anchor='nw')

        # Create indices table
        self.indices_table = ttk.Treeview(self.left_frame, columns=tuple(range(8)), show='headings', height=1)
        self.indices_table['columns'] = list(range(8))
        for i in range(8):
            self.indices_table.column(i, width=50)
            self.indices_table.heading(i, text=storage.headers[7 + i])
        self.indices_table.pack(anchor='w', expand=True)
        # for i in range(8):
        #     self.indices_table.heading(i, text=table.headers[7 + i])

        # Create fractions table
        self.fractions_table = ttk.Treeview(self.left_frame, columns=('0', '1'), show='headings', height=10)
        self.fractions_table.pack(anchor='w')
        self.fractions_table.heading('0', text='Fractions')
        self.fractions_table.heading('1', text='Weights')

        self.right_frame = Frame(self)
        self.right_frame.pack(side=RIGHT, anchor='nw')

        # Create cumulative curve plot
        self.curve = classes.Curve(self.right_frame)
        self.curve.curve_frame.pack(side=LEFT, expand=True, anchor='nw')

    def gather_info(self):
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

    def compute(self):
        fractions = db.upd_dict['fractions'][self.fractions_combobox.get()]
        weights = array(self.weight_entry.get().split(cfg.sep), dtype=float)
        cumulative_weights = cumsum(100 * weights / sum(weights)).round(cfg.rnd_frac)
        percentiles = (5, 16, 25, 50, 68, 75, 84, 95)
        phi = dict(zip(percentiles, interp(percentiles, cumulative_weights, fractions)))
        return fractions, cumulative_weights, storage.IndicesData(
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

    def check_sample(self) -> None:
        """
        Calculate cumulative weight of sand and indices, insert into tables

        :return: None
        """
        fractions, cumulative_weights, ind = self.compute()
        self.indices_table.delete(*self.indices_table.get_children())
        self.indices_table.insert('', 'end', values=ind.get())

        self.fractions_table.delete(*self.fractions_table.get_children())
        for i in range(len(fractions)):
            self.fractions_table.insert('', 'end', values=(fractions[i], cumulative_weights[i]))

        self.curve.update(fractions, cumulative_weights)

    def add_btn_cmd(self):
        db.add(*self.compute(), self.gather_info())

    def vali_date(self, value):
        pattern = r'[1|2][0-9]{3}\.[01][0-9]\.[0-3][0-9]'
        if re.fullmatch(pattern, value) is None:
            self.date_entry.config(fg='red')
            self.add_btn.config(state='disabled', text='Please use yyyy.mm.dd date format.')
            return False
        else:
            self.date_entry.config(fg='black')
            self.add_btn.config(state='normal', text='Add')
            return True


class CompareSamples(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        comp_table = classes.Table(self, columns=db.headers, scr_width=self.winfo_screenwidth(),
                                   scr_height=self.winfo_screenheight(), name='CompareSamples', tables=db.tables)
        comp_table.wrapper.pack()


class Settings(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.main = Frame(self)
        self.main.pack()
        self.set_lb = LabelFrame(self.main, text='General settings')
        self.set_lb.pack(fill='both')
        self.ind_rnd_label = Label(self.set_lb, text='Indices rounding')
        self.ind_rnd_label.grid(row=0, column=0)
        self.ind_rnd = ttk.Combobox(self.set_lb, values=('1', '2', '3', '4'), width=38)
        self.ind_rnd.insert(END, str(cfg.rnd_ind))
        self.ind_rnd.grid(row=0, column=1)

        self.frac_rnd_label = Label(self.set_lb, text='Fractions rounding')
        self.frac_rnd_label.grid(row=1, column=0)
        self.frac_rnd = ttk.Combobox(self.set_lb, values=('1', '2', '3', '4'), width=38)
        self.frac_rnd.insert(END, str(cfg.rnd_frac))
        self.frac_rnd.grid(row=1, column=1)

        self.sep_label = Label(self.set_lb, text='Separator')
        self.sep_label.grid(row=3, column=0)
        self.sep_entry = ttk.Combobox(self.set_lb, values=(' ', ', '), width=38)
        self.sep_entry.insert(END, cfg.sep)
        self.sep_entry.grid(row=3, column=1)

        self.fract_label = Label(self.set_lb, text='Default fractions')
        self.fract_label.grid(row=4, column=0)
        self.fract_cb = ttk.Combobox(self.set_lb, postcommand=upd_fract, values=list(db.upd_dict['fractions'].keys()),
                                     width=38)
        self.fract_cb.insert(END, cfg.def_fract)
        self.fract_cb.grid(row=4, column=1)
        # self.fract_del_button = Button(text='Delete selected', command=self.del_fractions)

        self.apply_button = Button(self.set_lb, text='Apply settings', command=self.apply)
        self.apply_button.grid(row=5, column=0)

        self.conv = LabelFrame(self.main, text='Converter')
        self.conv.pack(fill='both')

        self.inp_label = Label(self.conv, text='Input')
        self.inp_label.grid(row=0, column=0)
        self.inp = Entry(self.conv, width=48)
        self.inp.grid(row=0, column=1)
        self.outp_label = Label(self.conv, text='Output')
        self.outp_label.grid(row=1, column=0)
        self.outp = Entry(self.conv, width=48)
        self.outp.grid(row=1, column=1)

        self.convert_options = ['D(mm) to D(φ)', 'D(mm) to D(μ)', 'D(φ) to D(mm)', 'D(φ) to D(μ)', 'D(μ) to D(mm)',
                                'D(μ) to D(φ)']
        self.convert_combobox = ttk.Combobox(self.conv, values=self.convert_options)
        self.convert_combobox.grid(row=3, column=1)

        self.convert_button = Button(self.conv, text='Convert', command=self.convert)
        self.convert_button.grid(row=3, column=0)

        self.fract_lf = LabelFrame(self.main, text='Add fractions scheme')
        self.fract_lf.pack(fill='both')
        self.fract_name_label = Label(self.fract_lf, text='Name:')
        self.fract_name_label.grid(row=0, column=0)
        self.fract_name = Entry(self.fract_lf, width=49)
        self.fract_name.grid(row=0, column=1)
        self.fract_sch_label = Label(self.fract_lf, text='Scheme:')
        self.fract_sch_label.grid(row=1, column=0)
        self.fract_sch = Entry(self.fract_lf, width=49)
        self.fract_sch.grid(row=1, column=1)
        self.fract_add_button = Button(self.fract_lf, text='Add', command=self.add_fractoins)
        self.fract_add_button.grid(row=2, column=0)

    def convert(self):
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

    def apply(self):
        cfg.sep = self.sep_entry.get()
        cfg.rnd_ind = int(self.ind_rnd.get())
        cfg.rnd_frac = int(self.frac_rnd.get())
        cfg.def_fract = self.fract_cb.get()
        cfg.apply_settings()

    def add_fractoins(self):
        with open('fractions.txt', 'a') as f:
            f.write(f'{self.fract_name}: {self.fract_sch}')
        upd_fract()

    def del_fractions(self):
        db.upd_dict['fractions'].pop(key=self.fract_cb.get())


# class Help(ttk.Frame):
#     def __init__(self, container):
#         super().__init__(container)
#         lf_general = LabelFrame(self, text='General information')
#         lf_sample = LabelFrame(self, text='Sample tab')
#         lf_db = LabelFrame(self, text='Database tab')
#         lf_ref = LabelFrame(self, text='References')


def upd_fract():
    with open('fractions.txt', 'r') as f:
        for line in f:
            key, value = line.split(': ')
            value = array(value.split(), dtype=float)
            db.upd_dict['fractions'][key] = value


if __name__ == '__main__':
    # Create database, if not exists
    db.create_db()
    # Create config.txt dataclass
    cfg = storage.CFG()
    # Update config.txt dataclass from config.txt file
    cfg.update()
    # Update fractions from fractions.txt
    upd_fract()
    # create Tk main window
    app = App()
    app.mainloop()
