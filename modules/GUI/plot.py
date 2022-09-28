from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class Curve:
    """Plot of cumulative curve"""
    def __init__(self, container):
        # Create the frame for the plot
        self.__curve = Figure(figsize=(12, 8), dpi=100)
        # Insert the plot into tk frame
        self.__curve_canvas = FigureCanvasTkAgg(self.__curve, container)
        NavigationToolbar2Tk(self.__curve_canvas, container)
        # Configure the plot
        self.__axes = self.__curve.add_subplot(xscale='linear', yscale='linear', ybound=(0, 100))
        self.__axes.set_title('Cumulative curve')
        self.__axes.set_xlabel('Particle diameter, φ')
        self.__axes.set_ylabel('Cumulative weight %')
        self.__curve_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
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
