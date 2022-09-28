import tkinter as tk
from tkinter.ttk import Combobox
from modules.backend.converter import ConvertUnits


class Converter:
    __cfg = None
    __convert_options = ['D(mm) to D(φ)', 'D(mm) to D(μ)', 'D(φ) to D(mm)', 'D(φ) to D(μ)', 'D(μ) to D(mm)',
                         'D(μ) to D(φ)']

    def __init__(self, container, cfg):
        self.__cfg = cfg
        self.__conv = tk.LabelFrame(container, text='Converter')
        self.__conv.pack(fill='both')
        # Input and output
        self.__inp_label = tk.Label(self.__conv, text='Input')
        self.__inp_label.grid(row=0, column=0)
        self.__inp = tk.Entry(self.__conv, width=48)
        self.__inp.grid(row=0, column=1)
        self.__outp_label = tk.Label(self.__conv, text='Output')
        self.__outp_label.grid(row=1, column=0)
        self.__outp = tk.Entry(self.__conv, width=48)
        self.__outp.grid(row=1, column=1)
        # Convert mode
        self.__convert_combobox = Combobox(self.__conv, values=self.__convert_options)
        self.__convert_combobox.insert('end', self.__convert_options[0])
        self.__convert_combobox.grid(row=3, column=1)
        # "Convert" button
        self.__convert_button = tk.Button(self.__conv, text='Convert', command=self.__convert)
        self.__convert_button.grid(row=3, column=0)

    def __convert(self) -> None:
        """Converter function. Insert into output converted values."""
        inp = self.__inp.get().split(self.__cfg.separator)
        unit1, unit2 = self.__convert_combobox.get()[2:-1].replace(') to D(', ' ').split()
        self.__outp.delete(0, tk.END)
        self.__outp.insert(tk.END, ConvertUnits(inp, unit1, unit2, self.__cfg.separator).calculate())
