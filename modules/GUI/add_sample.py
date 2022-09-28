import tkinter as tk
from tkinter import ttk
import re
from modules.GUI.plot import Curve
from modules.GUI.multiple_entry import MultipleEntry
from modules.backend.storage import SampleData
from modules.backend.weights_indices_calc import WeightsAndIndices
from modules.backend.excel_import import ImportExcel


class AddSampleTab:
    """Sample tab"""
    frame = None
    __import_name = 'Import Excel file'

    def __init__(self, container, db, fract, cfg):
        self.frame = ttk.Frame(container)
        self.__db = db
        self.__cfg = cfg
        # Create left frame
        self.__left_frame = tk.Frame(self.frame)
        self.__left_frame.pack(side=tk.LEFT, anchor='nw', fill='y')
        # Frame for buttons
        self.__btn_frame = tk.Frame(self.__left_frame)
        # "Check" button
        self.__upd_btn = tk.Button(self.__btn_frame, text='Check', command=self.__check_sample)
        self.__upd_btn.grid(row=0, column=0)
        # "Add" button
        self.__add_btn = tk.Button(self.__btn_frame, text='Add', command=self.__add_btn_cmd)
        self.__add_btn.grid(row=0, column=1)
        self.__info = SampleInfoBlock(self.__left_frame, db, self.__add_btn)
        self.__weights_block = WeightsBlock(self.__left_frame, cfg, fract)
        self.__btn_frame.pack()
        # Create indices table
        self.__indices_table = ttk.Treeview(self.__left_frame, columns=tuple(range(8)), show='headings', height=1)
        self.__indices_table['columns'] = list(range(8))
        for i in range(8):
            self.__indices_table.column(i, width=50)
            self.__indices_table.heading(i, text=self.__db.headers[9 + i])
        self.__indices_table.pack(pady=20)
        # Create fractions table
        self.__fractions_table = ttk.Treeview(self.__left_frame, columns=('0', '1'), show='headings', height=10)
        self.__fractions_table.pack(anchor='n')
        self.__fractions_table.heading('0', text='Fractions')
        self.__fractions_table.heading('1', text='Weights')
        # Create right frame
        self.__right_frame = tk.Frame(self.frame)
        self.__right_frame.pack(anchor='nw')
        # Create cumulative curve plot in right frame
        self.__curve = Curve(self.__right_frame)
        self.imp = ImportExcel(db, cfg)
        self.__import_btn = tk.Button(self.__left_frame, text=self.__import_name,
                                      command=self.imp.import_worksheet)
        self.__import_btn.pack()

    def __check_sample(self) -> None:
        """
        Insert calculated data in tables and plot

        :return: None
        """
        fractions, cumulative_weights, ind = WeightsAndIndices(*self.__weights_block.get(), self.__cfg).get()
        # Update indices table
        self.__indices_table.delete(*self.__indices_table.get_children())
        self.__indices_table.insert('', 'end', values=ind.get())
        # Update fractions and cumulative weights table
        self.__fractions_table.delete(*self.__fractions_table.get_children())
        for i in range(len(fractions)):
            self.__fractions_table.insert('', 'end', values=(fractions[i], cumulative_weights[i]))
        # Update plot
        self.__curve.upd([fractions], [cumulative_weights], [self.__info.sample])

    def __add_btn_cmd(self) -> None:
        """Add info and calculated parameters into database"""
        self.__db.add_to_db(*WeightsAndIndices(*self.__weights_block.get(),
                                               self.__cfg).get(), self.__info.gather_info())
        self.__info.upd_combobox_values()


class SampleInfoBlock:
    __db = None

    """Block for gathering information about sample in Sample tab"""
    def __init__(self, root, db, add_btn):
        self.__db = db
        self.__add_btn = add_btn
        self.__info_frame = tk.Frame(root)
        self.__info_frame.pack(anchor='nw')
        # Collector
        self.__collector_label = tk.Label(self.__info_frame, text='Collector')
        self.__collector_label.grid(row=0, column=0, sticky='w')
        self.__collector_combobox = ttk.Combobox(self.__info_frame, width=37)
        self.__collector_combobox.grid(row=0, column=1)
        # Performer
        self.__performer_label = tk.Label(self.__info_frame, text='Performer')
        self.__performer_label.grid(row=1, column=0, sticky='w')
        self.__performer_combobox = ttk.Combobox(self.__info_frame, width=37)
        self.__performer_combobox.grid(row=1, column=1)
        # Sample
        self.__sample_label = tk.Label(self.__info_frame, text='Sample name')
        self.__sample_label.grid(row=2, column=0, sticky='w')
        self.__s_vcmd = (self.__info_frame.register(self.__validate_sample), '%P')
        self.__sample_entry = tk.Entry(self.__info_frame, validate='focusout', validatecommand=self.__s_vcmd, width=40)
        self.__sample_entry.grid(row=2, column=1)
        # Location
        self.__location_label = tk.Label(self.__info_frame, text='Location name')
        self.__location_label.grid(row=3, column=0, sticky='w')
        self.__location_combobox = ttk.Combobox(self.__info_frame, width=37)
        self.__location_combobox.grid(row=3, column=1)
        # Zone
        self.__zone_label = tk.Label(self.__info_frame, text='Zone')
        self.__zone_label.grid(row=4, column=0, sticky='w')
        self.__zone_combobox = ttk.Combobox(self.__info_frame, width=37)
        self.__zone_combobox.grid(row=4, column=1, )
        # Latitude
        self.__lat_label = tk.Label(self.__info_frame, text='Latitude')
        self.__lat_label.grid(row=5, column=0, sticky='w')
        self.__lat_entry = tk.Entry(self.__info_frame, width=40)
        self.__lat_entry.grid(row=5, column=1)
        # Longitude
        self.__lon_label = tk.Label(self.__info_frame, text='Longitude')
        self.__lon_label.grid(row=6, column=0, sticky='w')
        self.__lon_entry = tk.Entry(self.__info_frame, width=40)
        self.__lon_entry.grid(row=6, column=1)
        # Sampling date
        self.__date_label = tk.Label(self.__info_frame, text='Sampling date')
        self.__date_label.grid(row=7, column=0, sticky='w')
        self.__d_vcmd = (self.__info_frame.register(self.__vali_date), '%P')
        self.__date_entry = tk.Entry(self.__info_frame, width=40, validate='focusout', validatecommand=self.__d_vcmd)
        self.__date_entry.grid(row=7, column=1)
        self.upd_combobox_values()

    @property
    def sample(self):
        return self.__sample_entry.get()

    def upd_combobox_values(self):
        persons = self.__db.get_data('person')
        self.__collector_combobox['values'] = persons
        self.__performer_combobox['values'] = persons
        self.__zone_combobox['values'] = self.__db.get_data('zone')
        self.__location_combobox['values'] = self.__db.get_data('location')

    def gather_info(self) -> SampleData:
        """:return: SampleData dataclass with sample information"""
        return SampleData(
            collector=self.__collector_combobox.get(),
            performer=self.__performer_combobox.get(),
            sample=self.__sample_entry.get(),
            location=self.__location_combobox.get(),
            zone=self.__zone_combobox.get(),
            lat=self.__lat_entry.get(),
            lon=self.__lon_entry.get(),
            sampling_date=self.__date_entry.get()
        )

    def __vali_date(self, value: str) -> bool:
        pattern = r'[1|2][0-9]{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])'
        if re.fullmatch(pattern, value) is None:
            self.__vali_date_failed()
            return False
        else:
            self.__validation_confirmed(self.__date_entry)
            return True

    def __validate_sample(self, value: str) -> bool:
        if value in self.__db.get_data('sample'):
            self.__validate_sample_failed(value)
            return False
        else:
            self.__validation_confirmed(self.__sample_entry)
            return True

    def __vali_date_failed(self):
        self.__add_btn.config(state='disabled', text='Please use yyyy-mm-dd date format.')
        self.__date_entry.config(fg='red')

    def __validate_sample_failed(self, value):
        self.__add_btn.config(state='disabled', text=f'Sample "{value}" already exists')
        self.__sample_entry.config(fg='red')

    def __validation_confirmed(self, entry):
        entry.config(fg='black')
        self.__add_btn.config(state='normal', text='Add')


class WeightsBlock:
    """Block for gathering weights and calculation of indices"""
    def __init__(self,  root, cfg, fract):
        # Fractions and weights: Label and table of entry widgets
        self.__cfg = cfg
        self.__fract = fract
        self.__fractions_label = tk.Label(root, text='Fractions and weights:')
        self.__fractions_label.pack()
        self.__weight_entry = MultipleEntry(root, fract.schemes[cfg.fractions_scheme])
        self.__weight_entry.frame.pack()
        # Update entry table when tab is focused
        root.bind('<FocusIn>', self.__upd_fw)

    def __upd_fw(self, event) -> None:
        """Update fractions entry if scheme was modified in Settings"""
        if len(self.__weight_entry) != len(self.__fract.schemes[self.__cfg.fractions_scheme]):
            self.__weight_entry.upd(self.__fract.schemes[self.__cfg.fractions_scheme])

    def get(self):
        """:return: fractions and cumulative weights, indices values in IndicesData dataclass"""
        fractions = self.__fract.schemes[self.__cfg.fractions_scheme]
        weights = self.__weight_entry.get()
        return fractions, weights
