from contextlib import contextmanager
import openpyxl
from tkinter import filedialog


class ExportExcel:
    def __init__(self, db, trv):
        self.__db = db
        self.__trv = trv

    @staticmethod
    @contextmanager
    def __create_workbook():
        wb = openpyxl.Workbook()
        try:
            yield wb
        finally:
            wb.save(filename=f"{filedialog.asksaveasfilename(filetypes=(('Excel file', '*.xlsx'),))}.xlsx")

    def export(self):
        """Export as Excel .xlsx file"""
        with self.__create_workbook() as wb:
            # Active worksheet
            ws = wb.active
            ws.append(self.__db.headers)
            for i in self.__trv.get_children():
                # Read weights and fractions
                col = self.__db.run_query(
                    f'''
                            SELECT weight, fraction
                            FROM fractions
                                INNER JOIN samples USING(sample_id)
                            WHERE sample = "{self.__trv.item(i)['values'][4]}"
                        '''
                )
                # Append row in form: table row + weights + fractions
                ws.append(self.__trv.item(i)['values'] + ['weights:'] + [i[0] for i in col] +
                          ['fractions:'] + [i[1] for i in col])
