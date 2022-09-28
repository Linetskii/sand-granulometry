import tkinter as tk
from re import fullmatch


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
