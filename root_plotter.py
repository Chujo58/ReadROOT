import matplotlib.pyplot as plt
import mpl_scatter_density, numpy

class RootPlotter():
    """
    Matplotlib window to show 2D histograms. The data selected will also be shown in histograms on the side.

    Parameters
    ----------
    fig_size : tuple
        Size of the figure, normally in inches.
    """
    left, width = 0.1, 0.60
    bottom, height = 0.1, 0.60
    bottom_h = left_h = left + width + 0.02

    def __init__(self, fig_size: tuple) -> None:
        self.cmap = plt.get_cmap("white_turbo")
        rect_scatter = [self.left, self.bottom, self.width, self.height]
        rect_color = [self.left_h + 0.19, self.bottom, 0.02, self.height]
        rect_histx = [self.left, self.bottom_h, self.width, 0.17]
        rect_histy = [self.left_h, self.bottom, 0.17, self.height]
        
        self.figure = plt.figure(1, figsize=fig_size)
        self.axScatter = self.figure.add_axes(rect_scatter,projection="scatter_density")
        self.axHistx = self.figure.add_axes(rect_histx)
        self.axHisty = self.figure.add_axes(rect_histy)
        self.axColor = self.figure.add_axes(rect_color)

    def select_cmap(self, cmap_name: str) -> None:
        """
        Select the colormap to use for the 2D histogram.

        Parameters
        ----------
        cmap_name : str
            Name of the color map.
        """
        self.cmap = plt.get_cmap(cmap_name)

    def plot(self, data_x: numpy.array, data_y: numpy.array, bins: int) -> None:
        """
        Plots the selected data in the plot window.

        Parameters
        ----------
        data_x : numpy.array
            Data on the x axis.
        data_y : numpy.array
            Data on the y axis.
        bins : int
            Number of bins to use.
        """
        density = self.axScatter.scatter_density(data_x, data_y, cmap=self.cmap)
        self.axScatter.sharex(self.axHistx)
        self.axScatter.sharey(self.axHisty)

        self.figure.colorbar(density, self.axColor, label="Points per pixel")

        hist = numpy.histogram(data_x, bins)
        self.axHistx.plot(hist[1][1:],hist[0],drawstyle="steps-mid")
        self.axHistx.set_ylim(0, max(hist[0][10:]))

        hist = numpy.histogram(data_y, bins)
        self.axHisty.plot(hist[0],hist[1][1:],drawstyle="steps-mid")
        self.axHisty.set_xlim(0,max(hist[0][10:]))

        plt.setp(self.axHistx.get_xticklabels(), visible=False)
        plt.setp(self.axHisty.get_yticklabels(), visible=False)

        self.axScatter.set_xlim(0,bins)
        self.axScatter.set_ylim(0,bins)    

    def set_title(self, title: str):
        """Sets the title of the graph.

        Parameters
        ----------
        title : str
            Title of the graph
        """
        plt.suptitle(title)   

    def set_labels(self, x_label: str, y_label: str, hist_x: str, hist_y: str) -> None:
        """Sets the labels of the graph.

        Parameters
        ----------
        x_label : str
            2D histogram x label
        y_label : str
            2D histogram y label
        hist_x : str
            X axis histogram label
        hist_y : str
            Y axis histogram label
        """
        self.axScatter.set_xlabel(x_label)
        self.axScatter.set_ylabel(y_label)
        self.axHistx.set_ylabel(hist_x)
        self.axHisty.set_xlabel(hist_y)

    def show(self):
        """Shows the graph.
        """
        plt.show(block=True)