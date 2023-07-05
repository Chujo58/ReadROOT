"""
A package/class made to calculate uncertainties easily.
Made by Chloé Legué - Fall 2022
"""
import numpy as np
import matplotlib.pyplot as plt
import typing
from spinmob._data import fitter


def set_font_size(general_size,legend_size):
    plt.rcParams['font.size'] = general_size
    plt.rcParams['legend.fontsize'] = legend_size
    

class UFloat():
    def __init__(self, value: float, error: float) -> tuple:
        """
        Creates a UFloat value. This UFloat will contain the value and its uncertainty.

        Args:
            value (float): The value on which there is an uncertainty
            error (float): The uncertainty of the value
        """
        self._value = value
        self._error = abs(error)

    @staticmethod
    def first_digit(value: float) -> int:
        value = list(f"{value:.20f}")
        to_remove = 0
        for index, digit in enumerate(value):
            if digit == '0':
                continue
            if digit =='.':
                to_remove = 1
            else:
                return index - to_remove

    def __str__(self) -> str:
        length = self.first_digit(self._error)
        return f"({round(self._value,length)}±{round(self._error,length)})"

    def __add__(self, other):
        if type(other) != UFloat:
            other_value = other
            other_error = 0
        else:
            other_value = other._value
            other_error = other._error
        value = self._value + other_value
        error = np.sqrt(self._error**2 + other_error**2)
        return UFloat(value, error)

    def __sub__(self, other):
        if type(other) != UFloat:
            other_value = other
            other_error = 0
        else:
            other_value = other._value
            other_error = other._error
        value = self._value - other_value
        error = np.sqrt(self._error**2 + other_error**2)
        return UFloat(value, error)

    def __mul__(self, other):
        if type(other) != UFloat:
            other_value = other
            other_error = 0
        else:
            other_value = other._value
            other_error = other._error
        
        value = self._value * other_value
        # error = np.sqrt(((self._value+self._error)*other_value - value)**2 + (self._value*(other_value+other_error) - value)**2)
        error = value*np.sqrt((self._error/self._value)**2+(other_error/other_value)**2)
        return UFloat(value, error)

    def __pow__(self, other):
        if type(other) != UFloat:
            other_value = other
            other_error = 0
        else:
            other_value = other._value
            other_error = other._error
        
        value = self._value ** other_value
        # error = np.sqrt(((self._value+self._error)**other_value - value)**2 + (self._value**(other_value+other_error) - value)**2)
        error = (self._error/self._value)*other_value*value
        return UFloat(value, error)

    def __truediv__(self, other):
        if type(other) != UFloat:
            other_value = other
            other_error = 0
        else:
            other_value = other._value
            other_error = other._error

        value = self._value / other_value
        # error = np.sqrt(((self._value+self._error)/other_value - value)**2 + (self._value/(other_value+other_error) - value)**2)
        error = value*np.sqrt((self._error/self._value)**2+(other_error/other_value)**2)
        return UFloat(value, error)

    def __mod__(self, other):
        if type(other) != UFloat:
            other_value = other
            other_error = 0
        else:
            other_value = other._value
            other_error = other._error

        value = self._value % other_value
        error = np.sqrt(((self._value+self._error)%other_value - value)**2 + (self._value%(other_value+other_error))**2)
        return UFloat(value, error)

    def __lt__(self, other) -> bool:
        return self._value < other._value
    
    def __le__(self, other) -> bool:
        return self._value <= other._value

    def __eq__(self, other) -> bool:
        return self._value == other._value
    
    def __ne__(self, other) -> bool:
        return self._value != other._value

    def __gt__(self, other) -> bool:
        return self._value > other._value

    def __ge__(self, other) -> bool:
        return self._value >= other._value

    def evalf(self, func: callable):
        value = func(self._value)
        error = np.sqrt((func(self._value+self._error) - value)**2)
        return UFloat(value, error)

    def to_latex(self) -> str:
        length = self.first_digit(self._error)
        return f"({round(self._value,length)}\pm{round(self._error,length)})"

    def compare(self, theo) -> float:
        return abs(self._value-theo)/self._error


class UList(UFloat):
    def __init__(self, ufloats: list):
        self.list = []
        if len(ufloats) == 2:
            values, errors = ufloats
            if type(errors) == list:
                for index, item in enumerate(values):
                    self.list.append(UFloat(item,errors[index]))
            else:
                for item in values:
                    self.list.append(UFloat(item,errors))
        else:
            for item in ufloats:
                if type(item) == UFloat:
                    self.list.append(item)
    
    def __getitem__(self, item):
        return self.list[item]

    def __str__(self):
        string = ""
        for ufloat in self.list:
            string += str(ufloat) + ", "
        return string

    def append(self, ufloat: UFloat):
        if type(ufloat) == UFloat:
            self.list.append(ufloat)
        else:
            print('The item you are trying to append is not a UFloat.')
    def clear(self):
        self.list.clear()

    def copy(self):
        return self.list[::]

    def count(self):
        return self.list.count()

    def extend(self, ulist):
        correct = False
        for item in ulist:
            if type(item) == UFloat:
                correct = True
            else:
                correct = False
        if correct:
            self.list.extend(ulist)
    
    def index(self, ufloat):
        return self.list.index(ufloat)

    def insert(self, ufloat, position):
        if type(ufloat) == UFloat:
            self.list.insert(position, ufloat)

    def pop(self, position):
        if position >= len(self.list):
            print('Cannot remove this object.')
        else:
            return self.list.pop(position)

    def remove(self, position):
        if position >= len(self.list):
            print('Cannot remove this object.')
        else:
            self.list.remove(position)

    def reverse(self):
        self.list.reverse()

    def get_values(self):
        return [item._value for item in self.list]

    def get_errors(self):
        return [item._error for item in self.list]

    def sort(self,sort_by):
        if sort_by == 'value':
            values = self.get_values()
            sorted_ = values.copy()
            sorted_.sort()
            indexes = []
            for value in sorted_:
                indexes.append(values.index(value))

            sorted_list = []
            for index in indexes:
                sorted_list.append(self.list[index])
        if sort_by == 'error':
            errors = self.get_errors()
            sorted_ = errors.copy()
            sorted_.sort()
            indexes = []
            for value in sorted_:
                indexes.append(errors.index(value))

            sorted_list = []
            for index in indexes:
                sorted_list.append(self.list[index])
        else:
            print(f'Cannot sort with the {sort_by} filter mentioned.')

        


# Ulist = list[UFloat]

def get_lists(list_: UList) -> typing.Tuple[list[float],list[float]]:
    """
    Gets the values and uncertainties of a `UList` (`list[UFloat]`).

    Args:
        list_ (UList): List of `UFloat`

    Returns:
        typing.Tuple[list[float],list[float]]: Two lists containing the values and uncertainties respectively.
    """
    temp_list = []
    temp_list2 = []
    for value in list_:
        temp_list.append(value._value)
        temp_list2.append(value._error)
    return temp_list, temp_list2

def weighted_mean(list_: UList) -> UFloat:
    """
    Calculates the weighted mean of a `UList` (`list[UFloat]`).

    Args:
        list_ (UList): List of `UFloat`.

    Returns:
        UFloat: Result of the weighted mean.
    """
    values, uncertainties = list_.get_values(), list_.get_errors()
    err = np.sqrt(1/np.sum([1/a**2 for a in uncertainties]))
    mean = (err**2)*np.sum([(value)/((uncertainties[index])**2) for index, value in enumerate(values)])
    return UFloat(mean, err)


class UPlot():
    def __init__(self, subplots=None, mosaic=False,share_x=False,share_y=False):
        self.lines = {}
        self.lines_number = {}
        self.lines_data = {}
        # self.lines_kwargs = {}
        self.number = 0
        if mosaic:
            if subplots is not None:
                self.figure, self.axs = plt.subplot_mosaic(mosaic=subplots)#,sharex=share_x,sharey=share_y)
            else:
                self.figure, self.axs = plt.subplot_mosaic(mosaic='A')#,sharex=share_x,sharey=share_y)
        else:
            if subplots is not None:
                self.figure, self.axs = plt.subplots(subplots,sharex=share_x,sharey=share_y)
            else:
                self.figure, self.axs = plt.subplots(1,sharex=share_x,sharey=share_y)

    
    def fit(self, line_name: str, function: str, call: callable, parameters: str, plot=False, plot_res=False, subplot=None, subplot_res=None, **func_kwargs):
        xdata, ydata = self.lines_data.get(line_name)
        fitter_obj = fitter()
        fitter_obj['autoplot'] = plot
        x = xdata.get_values()
        x_err = xdata.get_errors()
        y = ydata.get_values()
        y_err = ydata.get_errors()
        x_range = np.linspace(min(x),max(x),1000)
        fitter_obj.set_data(x,y,y_err)
        fitter_obj.set_functions(function, parameters, **func_kwargs)
        fitter_obj.fit()

        fit_params = fitter_obj.get_fit_parameters()
        ufloat_params = [UFloat(item.value,item.stderr) for item in fit_params]
        y_range = [call(i, *ufloat_params) for i in x_range]
        # print(y_range)
        # ys = [item for item in y_range]
        # print(ys)
        y_values, error = get_lists(y_range)
        if subplot is not None:
            str_params = ""
            str_params_name = parameters.split(',')
            for index, param in enumerate(ufloat_params):
                str_params += str_params_name[index] + "=" + str(param) + "," 
            self.axs[subplot].plot(x_range,y_values,label=f'{line_name} : {function},{str_params}')
            self.axs[subplot].legend()
        else:
            str_params = ""
            str_params_name = parameters.split(',')
            for index, param in enumerate(ufloat_params):
                str_params += str_params_name[index] + "=" + str(param) + "," 
            self.axs.plot(x_range,y_values,label=f'{line_name}:{function},{str_params}')
            self.axs.legend()

        if plot_res:
            residuals = UList([UFloat(y[index],y_err[index]) - call(UFloat(value,x_err[index]),*ufloat_params) for index, value in enumerate(x)])
            if subplot_res is not None:
                res_values = residuals.get_values()
                res_errors = residuals.get_errors()
                self.axs[subplot_res].errorbar(x,res_values,yerr=res_errors,label=f'{line_name} : Residuals', ecolor='black',fmt='.',ms=25)
        print('-'*15)
        print(f"{line_name} Fit")
        print('-'*15)
        print(fitter_obj)
        return fitter_obj

    def move_legend(self, position: str, alpha: int, subplot=None):
        if subplot is not None:
            self.axs[subplot].legend(loc=position, framealpha=alpha)
        else:
            self.axs.legend(loc=position, framealpha=alpha)

    def set_xlabel(self,label: str, subplot=None):
        if subplot is not None:
            self.axs[subplot].set_xlabel(label)
        else:
            self.axs.set_xlabel(label)

    def set_ylabel(self,label: str, subplot=None):
        if subplot is not None:
            self.axs[subplot].set_ylabel(label)
        else:
            self.axs.set_ylabel(label)

    def set_labels(self,x_label,y_label,subplot=None):
        if subplot is not None:
            self.set_xlabel(x_label,subplot)
            self.set_ylabel(y_label,subplot)
        else:
            self.set_xlabel(x_label)
            self.set_ylabel(x_label)

    def set_title(self,title,subplot=None):
        if subplot is not None:
            self.axs[subplot].set_title(title)
        else:
            self.axs.set_title(title)

    def set_figsize(self,fig_size: tuple):
        self.figure.set_size_inches(*fig_size)

    def get_lines(self):
        return self.axs.get_lines()

    def remove_line(self, name):
        num = self.lines_number.get(name)
        self.axs.lines.remove(self.axs.lines[num])

    def add_point(self,x,y,name,subplot=None,**kwargs):
        if subplot is not None:
            self.axs[subplot].scatter(x,y,label=name,**kwargs)
        else:
            self.axs.scatter(x,y,label=name,**kwargs)
    
    def clear(self):
        self.axs.cla()

    def show(self):
        plt.show()


class UScatter(UPlot):
    def __init__(self, subplots=None, mosaic=False,share_x=False,share_y=False):
        super().__init__(subplots,mosaic,share_x,share_y)
    def add_scatter(self, xdata: UList, ydata: UList, name: str, xlabel: str, ylabel: str, title: str, subplot=None, **kwargs):
        """
        Adds an errorbar plot to the selected subplot.

        Args:
            xdata (UList): x values to be plotted
            ydata (UList): y values to be plotted
            name (str): Name of the line (Used by some other functions)
            xlabel (str): Label of the x axis
            ylabel (str): Label of the y axis
            title (str): Title of the subplot
            subplot (int/str, optional): Subplot selected. Defaults to None.
        """
        if subplot is not None:
            x = xdata.get_values()
            x_err = xdata.get_errors()
            y = ydata.get_values()
            y_err = ydata.get_errors()
            self.lines[name] = self.axs[subplot].errorbar(x,y,yerr=y_err,xerr=x_err,label=name,**kwargs)
            self.axs[subplot].set_xlabel(xlabel)
            self.axs[subplot].set_ylabel(ylabel)
            self.axs[subplot].set_title(title)
            self.lines_number[name] = self.number
            self.lines_data[name] = [xdata,ydata]
        else:
            x = xdata.get_values()
            x_err = xdata.get_errors()
            y = ydata.get_values()
            y_err = ydata.get_errors()
            self.lines[name] = self.axs.errorbar(x,y,yerr=y_err,xerr=x_err,label=name,**kwargs)
            self.axs.set_xlabel(xlabel)
            self.axs.set_ylabel(ylabel)
            self.axs.set_title(title)
            self.lines_number[name] = self.number
            self.lines_data[name] = [xdata,ydata]
        
        self.number += 1


if __name__ == "__main__":
    a = UList([UFloat(1, 1),UFloat(2, 1),UFloat(3, 0.5)])
    b = UList([UFloat(1,0.5),UFloat(2,0.5),UFloat(2.5,0.3)])
    test = UScatter(1)
    test.add_scatter(a, b, 'test', 'x','y','title', fmt='.',ecolor='grey',ms=25)
    def func(x,a,b):
        return a*x**2+b
    test.fit('test', 'a*x**2+b',func,'a,b')
    test.show()
    print(test.get_lines())
    plt.rc