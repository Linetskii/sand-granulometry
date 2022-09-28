import tkinter as tk
from tkinter import ttk
from modules.GUI.converter import Converter


class Settings:
    """
    Settings tab
    """
    frame = None
    __cfg = None
    __fract = None

    def __init__(self, container, cfg, fract):
        self.frame = ttk.Frame(container)
        self.__cfg = cfg
        self.__fract = fract
        # Little frame to align blocks
        self.__main = tk.Frame(self.frame)
        self.__main.pack()
        self.__general = GeneralSettings(self.__main, self.__cfg, self.__fract)
        self.__conv = Converter(self.__main, cfg)
        # Add fractions
        self.__fract = AddFractions(self.__main, self.__fract)


class GeneralSettings:
    def __init__(self, container, cfg, fract):
        self.__cfg = cfg
        self.__fract = fract
        # General settings LabelFrame
        self.__settings_lframe = tk.LabelFrame(container, text='General settings')
        self.__settings_lframe.pack(fill='both')
        # Zoom
        self.__zoom_label = tk.Label(self.__settings_lframe, text='Window')
        self.__zoom_label.grid(row=5, column=0)
        self.__zoom_combo = ttk.Combobox(self.__settings_lframe, values=('fullscreen', 'windowed'), width=38)
        self.__zoom_combo.insert(tk.END, 'fullscreen' if self.__cfg.zoomed == 'zoomed' else 'windowed')
        self.__zoom_combo.grid(row=5, column=1)
        # Indices rounding
        self.__indices_round_label = tk.Label(self.__settings_lframe, text='Indices rounding')
        self.__indices_round_label.grid(row=0, column=0)
        self.__indices_round = ttk.Combobox(self.__settings_lframe, values=('1', '2', '3', '4'), width=38)
        self.__indices_round.insert(tk.END, str(self.__cfg.indices_rounding))
        self.__indices_round.grid(row=0, column=1)
        # Weights rounding
        self.__fract_round_label = tk.Label(self.__settings_lframe, text='Weights rounding')
        self.__fract_round_label.grid(row=1, column=0)
        self.__fract_round = ttk.Combobox(self.__settings_lframe, values=('1', '2', '3', '4'), width=38)
        self.__fract_round.insert(tk.END, str(self.__cfg.fractions_rounding))
        self.__fract_round.grid(row=1, column=1)
        # Separator. Currently, used only in next two blocks.
        self.__sep_label = tk.Label(self.__settings_lframe, text='Separator')
        self.__sep_label.grid(row=3, column=0)
        self.__sep_entry = ttk.Combobox(self.__settings_lframe, values=(' ', ', '), width=38)
        self.__sep_entry.insert(tk.END, self.__cfg.separator)
        self.__sep_entry.grid(row=3, column=1)
        # Fractions scheme selection
        self.__fract_label = tk.Label(self.__settings_lframe, text='Select fractions scheme')
        self.__fract_label.grid(row=4, column=0)
        self.__fract_cb = ttk.Combobox(self.__settings_lframe, postcommand=self.__upd_fractions, width=38)
        self.__fract_cb.insert(tk.END, self.__cfg.fractions_scheme)
        self.__fract_cb.grid(row=4, column=1)
        # Apply Button
        self.__apply_button = tk.Button(self.__settings_lframe, text='Apply settings', command=self.__apply)
        self.__apply_button.grid(row=6, column=0, sticky='w')

    def __apply(self) -> None:
        """Apply settings: write it to the config.txt, update cfg"""
        self.__cfg.apply_settings(self.__sep_entry.get(),
                                  self.__indices_round.get(),
                                  self.__fract_round.get(),
                                  self.__fract_cb.get(),
                                  self.__zoom_combo.get()
                                  )

    def __upd_fractions(self) -> None:
        """Update fractions combobox"""
        self.__fract_cb['values'] = list(i for i in self.__fract.schemes.keys())


class AddFractions:
    def __init__(self, container, fract):
        self.__fract = fract
        # Add fractions
        self.__fract_lf = tk.LabelFrame(container, text='Add fractions scheme')
        self.__fract_lf.pack(fill='both')
        # Name
        self.__fract_name_label = tk.Label(self.__fract_lf, text='Name:')
        self.__fract_name_label.grid(row=0, column=0)
        self.__fract_name = tk.Entry(self.__fract_lf, width=49)
        self.__fract_name.grid(row=0, column=1)
        # Scheme
        self.__fract_sch_label = tk.Label(self.__fract_lf, text='Scheme:')
        self.__fract_sch_label.grid(row=1, column=0)
        self.__fract_sch = tk.Entry(self.__fract_lf, width=49)
        self.__fract_sch.grid(row=1, column=1)
        # Add button
        self.__fract_add_button = tk.Button(self.__fract_lf, text='Add', command=self.__add_fractions)
        self.__fract_add_button.grid(row=2, column=0, sticky='w')

    def __add_fractions(self) -> None:
        """
        Add fractions to the fractions.txt, update Fractions
        """
        self.__fract.schemes = (self.__fract_name.get(), self.__fract_sch.get())
