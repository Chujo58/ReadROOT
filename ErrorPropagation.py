"""
A package/class made to calculate uncertainties easily.
Made by Chloé Legué - Fall 2022
V2
"""
import numpy as np
import matplotlib.pyplot as plt
import typing
from spinmob._data import fitter
from scipy.optimize import curve_fit as cf
from scipy.stats import poisson, norm
from scipy.special import factorial as fc

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
        item = list(f"{value:.60f}")
        to_remove = 0
        final_digit = 0
        for index, digit in enumerate(item):
            if digit == '0':
                continue
            if digit =='.':
                to_remove = 1
            else:
                final_digit = index - to_remove
                break
        
                # print(f"{round(value*10**final_digit,1):.2e}") Petits trucs
        # print(final_digit)
        return final_digit

    # def scale(self) -> int:
    #     scaling = float(str(1/self._value)[0:str(1/self._value).find('e')])
    #     smallest_digit = self.first_digit(self._error)
    #     scaled_value = int(scaling*self._value) if smallest_digit == 0 else scaling*self._value
    #     return scaled_value

    #print and str functions
    def __str__(self) -> str:
        # scale = self.scale()
        length = self.first_digit(self._error)#/scale)
        # return f"({self._value/scale:.{length}f}±{self._error/scale:.{length}f})"
        return f"({round(self._value,length)}±{round(self._error,length)})"

    #Mathematical functions
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

    def __radd__(self, other):
        return UFloat.__add__(self, other)

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

    def __rsub__(self, other):
        return UFloat.__sub__(self, other)*-1

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

    def __rmul__(self, other):
        return UFloat.__mul__(self, other)

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

    def __rtruediv__(self, other):
        return UFloat.__truediv__(self, other)**(-1)

    def __mod__(self, other):
        if type(other) != UFloat:
            other_value = other
            other_error = 0
        else:
            other_value = other._value
            other_error = other._error

        value = self._value % other_value
        print(value)
        error = np.sqrt(((self._value+self._error)%other_value - value)**2 + (self._value%(other_value+other_error))**2)
        return UFloat(value, error)

    #Comparison functions
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

    #Operator= functions
    def __iadd__(self, other):
        return UFloat.__add__(self, other)

    def __isub__(self, other):
        return UFloat.__sub__(self, other)

    def __imul__(self, other):
        return UFloat.__mul__(self, other)

    def __idiv__(self, other):
        return UFloat.__truediv__(self, other)

    def __imod__(self, other):
        return UFloat.__mod__(self, other) 
    
    def __ipow__(self, other):
        return UFloat.__pow__(self, other)

    #Other functions
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
    def __init__(self, **kwargs):
        """
        Creates a `UList`. The `kwargs` can only have the following arguments: `values` containing the values of your data, `errors` containing the errors of your data (as a single float or as a list of floats) and `ufloats` containing the data already formatted into `UFloat`.
        """
        self.list = []
        self.keys = ['values','errors','ufloats']
        for key in kwargs:
            if key not in self.keys:
                raise KeyError(f"You cannot use '{key}' to initialize a UList.")
        if 'values' in kwargs.keys() and 'errors' in kwargs.keys():
            if type(kwargs.get('errors')) == float:
                error = kwargs.get('errors')
                for value in kwargs.get('values'):
                    self.list.append(UFloat(value,error))
            if type(kwargs.get('errors')) == int:
                error = kwargs.get('errors')
                for value in kwargs.get('values'):
                    self.list.append(UFloat(value,error))
            if type(kwargs.get('errors')) == list:
                if len(kwargs.get('errors')) != len(kwargs.get('values')):
                    raise ValueError(f"The length of the errors, {len(kwargs.get('errors'))}, doesn't match the length of the values, {len(kwargs.get('values'))}.")
                else:
                    for index, value in enumerate(kwargs.get('values')):
                        self.list.append(UFloat(value,kwargs.get('errors')[index]))
            elif type(kwargs.get('errors')) != list and type(kwargs.get('errors')) != int and type(kwargs.get('errors')) != float:
                raise TypeError(f"The type of the errors, {type(kwargs.get('errors'))}, cannot initialize a UList.")

        elif 'values' in kwargs.keys() and 'errors' not in kwargs.keys():
            raise Exception("You cannot initialize a UList with values but without errors.")

        if 'ufloats' in kwargs.keys():
            if type(kwargs.get('ufloats')) == list:
                for item in kwargs.get('ufloats'):
                    if type(item) == UFloat:
                        self.list.append(item)
            if type(kwargs.get('ufloats')) == UFloat:
                self.list.append(kwargs.get('ufloats'))

        if kwargs == None:
            pass
    
    def __len__(self):
        return len(self.list)
    
    def __getitem__(self, item):
        return self.list[item]

    def __str__(self):
        string = ""
        for ufloat in self.list:
            string += str(ufloat) + ", "
        return string

    def __add__(self, other):
        # total = []
        if type(other) == UList:
            if len(other) == len(self):
                for index, ufloat in enumerate(self.list):
                    self.list[index] += other.list[index]
        if type(other) != UList:
            if type(other) == list:
                for index, ufloat in enumerate(self.list):
                    self.list[index] += other[index]
            else:
                for index, ufloat in enumerate(self.list):
                    self.list[index] += other

        return self

    def __radd__(self, other):
        return UList.__add__(self, other)

    def __iadd__(self, other):
        return UList.__add__(self, other)

    def __sub__(self, other):
        if type(other) == UList:
            if len(other) == len(self):
                for index, ufloat in enumerate(self.list):
                    self.list[index] -= other.list[index]

        if type(other) != UList:
            if type(other) == list:
                for index, ufloat in enumerate(self.list):
                    self.list[index] -= other[index]
            else:
                for index, ufloat in enumerate(self.list):
                    self.list[index] -= other

        return self

    def __rsub__(self, other):
        return UList.__sub__(self, other)

    def __isub__(self, other):
        return UList.__sub__(self, other)

    def __mul__(self, other):
        if type(other) == UList:
            if len(other) == len(self):
                for index, ufloat in enumerate(self.list):
                    self.list[index] *= other.list[index]
        if type(other) != UList:
            if type(other) == list:
                for index, ufloat in enumerate(self.list):
                    self.list[index] *= other[index]
            else:
                for index, ufloat in enumerate(self.list):
                    self.list[index] *= other

        return self

    def __rmul__(self, other):
        return UList.__mul__(self, other)

    def __imul__(self, other):
        return UList.__mul__(self, other)

    def __truediv__(self, other):
        if type(other) == UList:
            if len(other) == len(self):
                for index, ufloat in enumerate(self.list):
                    self.list[index] /= other.list[index]
        if type(other) != UList:
            if type(other) == list:
                for index, ufloat in enumerate(self.list):
                    self.list[index] /= other[index]
            else:
                for index, ufloat in enumerate(self.list):
                    self.list[index] /= other

        return self

    def __rtruediv__(self, other):
        return UList.__truediv__(self, other)**(-1)

    def __idiv__(self, other):
        return UList.__truediv__(self, other)

    def __pow__(self, other):
        if type(other) == UList:
            if len(other) == len(self):
                for index, ufloat in enumerate(self.list):
                    self.list[index] **= other.list[index]
        if type(other) != UList:
            if type(other) == list:
                for index, ufloat in enumerate(self.list):
                    self.list[index] **= other[index]
            else:
                for index, ufloat in enumerate(self.list):
                    self.list[index] **= other
        
        return self

    def __ipow__(self, other):
        return UList.__pow__(self, other)

    def __mod__(self, other):
        if type(other) == UList:
            if len(other) == len(self):
                for index, ufloat in enumerate(self.list):
                    self.list[index] %= other.list[index]
        if type(other) != UList:
            if type(other) == list:
                for index, ufloat in enumerate(self.list):
                    self.list[index] %= other[index]
            else:
                for index, ufloat in enumerate(self.list):
                    self.list[index] %= other
        
        return self

    def __imod__(self, other):
        return UList.__mod__(self, other)

    def sum(self):
        total = 0
        for ufloat in self.list:
            total += ufloat
        return total
        
    def append(self, **kwargs):
        for key in kwargs:
            if key not in self.keys:
                raise KeyError(f"You cannot use {key} to add an item to a UList.")
        
        if 'value' in kwargs.keys() and 'error' in kwargs.keys():
            if type(kwargs.get('value')) == int or type(kwargs.get('value')) == float:
                if type(kwargs.get('error')) == int or type(kwargs.get('error')) == float:
                    self.list.append(UFloat(kwargs.get('value'),kwargs.get('error')))
        else:
            raise Exception("You cannot append an item with value but without error.")

        if 'ufloats' in kwargs.keys():
            if type(kwargs.get('ufloat')) == UFloat:
                self.list.append(kwargs.get('ufloat'))

    def clear(self):
        self.list.clear()

    def copy(self):
        return UList(ufloats=self.list.copy())

    def count(self,ufloat):
        return self.list.count(ufloat)

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

    def get_data(self):
        return self.get_values(), self.get_errors()  

    def to_latex(self, table_label: str, rows: int, columns: int, headers_position: str, table_headers: list, table_caption: str):
        final_str = "\\begin{table}\n\\begin{tabular}"
        format_ = "{" + (columns-1)*"c|" + "c}"
        mid_str = "\n"
        end_str = "\n\\end{tabular}\n\\end{table}"
        if headers_position == 'vertical':
            if len(table_headers) != rows:
                raise Exception(f"Size mismatch for table headers and rows: {len(table_headers)} & {rows}")
            if len(table_headers) == rows:
                for index in range(0, len(self.list),columns):
                    for sub_index in range(0,columns):
                        if sub_index == 0:
                            mid_str += f"{table_headers[index]} &"
                        if 0 < sub_index and sub_index <= columns - 2:
                            mid_str += f"{str(self.list[sub_index-1])} &"
                        if sub_index == columns - 1:
                            mid_str += f"{str(self.list[sub_index-1])}\\\\ "




        return final_str+format_+mid_str+end_str


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

def standard_dev(list_: UList, mean: UFloat) -> UFloat:
    sum = 0
    for ufloat in list_:
        sum += (ufloat-mean)**2

    return (sum/(len(list_)-1)).evalf(np.sqrt)

class UPlot():
    def __init__(self, subplots=None, mosaic=False,share_x=False,share_y=False):
        self.lines = {}
        self.lines_number = {}
        self.lines_data = {}
        self.number = 0
        self.items = {}
        # self.legends = {}
        if mosaic:
            if subplots is not None:
                self.figure, self.axs = plt.subplot_mosaic(mosaic=subplots,sharex=share_x,sharey=share_y)
            else:
                self.figure, self.axs = plt.subplot_mosaic(mosaic='A',sharex=share_x,sharey=share_y)
        else:
            if subplots is not None:
                self.figure, self.axs = plt.subplots(subplots,sharex=share_x,sharey=share_y)
            else:
                self.figure, self.axs = plt.subplots(1,sharex=share_x,sharey=share_y)

        self.marker_size = 5
        self.fit_lines = {}


    @staticmethod
    def poisson(x, mean, scale):
        return scale*poisson.pmf(x, mean)

    @staticmethod
    def poisson_plot(x, mean, scale):
        return scale*np.exp(-mean)*mean**x/fc(x)

    @staticmethod
    def gaussian(x, mean, sigma, scale):
        return scale*np.exp(-1/2*((x-mean)/sigma)**2)

    def change_figure_size(self, width, height):
        self.figure.set_size_inches(width, height)

    def change_marker_size(self, marker_size):
        self.marker_size = marker_size

    def change_line_fit(self,name: str,**kwargs):
        if 'residuals' in name:
            if 'ecolor' in kwargs:
                caps = self.fit_lines.get(name)[1]
                [cap.set_color(kwargs.get('ecolor')) for cap in caps]
                bars = self.fit_lines.get(name)[2]
                [bar.set_color(kwargs.get('ecolor')) for bar in bars]                
                    # line.set(color=kwargs.get('ecolor'))
            else:
                line = self.fit_lines.get(name)[0]
                line.set(**kwargs)
        else:
            line = self.fit_lines.get(name)[0]
            line_res = self.fit_lines.get(f"{name}-residuals")[0]
            if line is not None:
                line.set(**kwargs)
            if line_res is not None:
                line_res.set(**kwargs)
                line_res.set(linestyle='None')
    
    def fit(self, line_name: str, fit_name: str, function: str, call: callable, parameters: str, plot=False, plot_res=False, subplot=None, subplot_res=None, **func_kwargs):
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
            self.fit_lines[fit_name] = self.axs[subplot].plot(x_range,y_values,label=f'{line_name} : {function},{str_params}')
            # self.axs[subplot].legend()
        else:
            str_params = ""
            str_params_name = parameters.split(',')
            for index, param in enumerate(ufloat_params):
                str_params += str_params_name[index] + "=" + str(param) + "," 
            self.fit_lines[fit_name] = self.axs.plot(x_range,y_values,label=f'{line_name}:{function},{str_params}')
            # self.axs.legend()

        if plot_res:
            residuals = UList(ufloats=[UFloat(y[index],y_err[index]) - call(UFloat(value,x_err[index]),*ufloat_params) for index, value in enumerate(x)])
            if subplot_res is not None:
                res_values = residuals.get_values()
                res_errors = residuals.get_errors()
                self.fit_lines[f"{fit_name}-residuals"] = self.axs[subplot_res].errorbar(x,res_values,yerr=res_errors,label=f'{line_name} : Residuals', ecolor='black',fmt='.',ms=self.marker_size)
        
        print('-'*15)
        print(f"{line_name} Fit")
        print('-'*15)
        print(fitter_obj)
        return ufloat_params, fitter_obj

    def fit_poisson(self, line_name: str, fit_name: str, plot_res=False, subplot=None, subplot_res=None, use_old = False):
        xdata, ydata = self.lines_data.get(line_name)
        x = xdata.get_values()
        xerr = xdata.get_errors()
        y = ydata.get_values()
        yerr = ydata.get_errors()
        for index, item in enumerate(yerr):
            if item == 0:
                yerr[index] = 1
        mean_init = x[y.index(max(y))] #Initial guess for the mean.
        if use_old:
            params, pcov = cf(self.poisson,x,y,sigma=yerr,absolute_sigma=True,p0=[mean_init,max(y)])
            residuals =  UList(ufloats=[ydata[index]-self.poisson(x[index], *params) for index in range(0,len(y))])
        else:
            params, pcov = cf(self.poisson_plot,x,y,sigma=yerr,absolute_sigma=True,p0=[mean_init,max(y)])
            residuals =  UList(ufloats=[ydata[index]-self.poisson_plot(x[index], *params) for index in range(0,len(y))])

        params_err = np.sqrt(np.diag(pcov))
        
        # chisqr_res = residuals.copy()
        chi_sqr = ((residuals.copy()/yerr)**2).sum()
        label_legend = f"Poisson Fit: ν={str(UFloat(params[0], np.sqrt(params[0])))}, Scale={str(UFloat(params[1],params_err[1]))}, χ2={str(chi_sqr)}"


        #Simulate points for the fit:
        if use_old:
            x_range = x
        else:
            x_range = np.linspace(min(x), max(x), 100)

        if subplot is not None:
            if use_old:
                self.fit_lines[fit_name] = self.axs[subplot].plot(x_range,self.poisson(x_range,*params),label=label_legend)
            else:
                self.fit_lines[fit_name] = self.axs[subplot].plot(x_range,self.poisson_plot(x_range,*params),label=label_legend)
            # self.axs[subplot].legend()
        else:
            if use_old:
                self.fit_lines[fit_name] = self.axs[subplot].plot(x_range,self.poisson(x_range,*params),label=label_legend)
            else:
                self.fit_lines[fit_name] = self.axs[subplot].plot(x_range,self.poisson_plot(x_range,*params),label=label_legend)
 
        if plot_res:
            sum_ = (residuals.copy()**2).sum()
            # sum_ = 0
            # for val in residuals:
                # sum_ += val**2
            print('σ (theo?)',(sum_/(len(residuals)-1)).evalf(np.sqrt)._value)
            if subplot_res is not None:
                res_values = residuals.get_values()
                res_errors = residuals.get_errors()
                self.fit_lines[f"{fit_name}-residuals"] = self.axs[subplot_res].errorbar(x,res_values,yerr=res_errors,label=f"{line_name} : Residuals from Poisson Fit", ecolor='black', fmt='.',ms=self.marker_size)
                # self.axs[subplot_res].legend()

        parameters = UList(ufloats=[UFloat(value, params_err[index]) if index != 0 else UFloat(value, np.sqrt(value)) for index, value in enumerate(params)])
        return parameters

    def fit_gaussian(self, line_name: str, fit_name: str, plot_res=False, subplot=None, subplot_res=None):
        xdata, ydata = self.lines_data.get(line_name)
        x, xerr = xdata.get_data()
        y, yerr = ydata.get_data()
        for index, item in enumerate(yerr):
            if item == 0:
                yerr[index] = 1
        mean_init = x[y.index(max(y))] #Initial guess for the mean.
        sigma_init = max(x)-min(x)

        params, pcov = cf(self.gaussian,x,y,sigma=yerr,absolute_sigma=True,p0=[mean_init,sigma_init,max(y)])
        params_err = np.sqrt(np.diag(pcov))
        residuals =  UList(ufloats=[ydata[index]-self.gaussian(x[index], *params) for index in range(0,len(y))])
        chi_sqr = ((residuals.copy()/yerr)**2).sum()
        label_legend = f"Gaussian Fit: μ={str(UFloat(params[0], params_err[0]))}, σ={str(UFloat(params[1], params_err[1]))}, Scale={str(UFloat(params[2], params_err[2]))}, χ2={str(chi_sqr)}"

        #Simulate points for the fit:
        x_range = np.linspace(min(x),max(x),1000)

        if subplot is not None:
            self.fit_lines[fit_name] = self.axs[subplot].plot(x_range,self.gaussian(x_range,*params),label=label_legend)
            # self.axs[subplot].legend()

        else:
            self.fit_lines[fit_name] = self.axs.plot(x_range,self.gaussian(x_range,*params),label=label_legend)
            # self.axs.legend()

        if plot_res:
            if subplot_res is not None:
                res_values = residuals.get_values()
                res_errors = residuals.get_errors()
                self.fit_lines[f"{fit_name}-residuals"] = self.axs[subplot_res].errorbar(x,res_values,yerr=res_errors,label=f"{line_name} : Residuals from Gaussian Fit", ecolor='black', fmt='.',ms=self.marker_size)
                # self.axs[subplot_res].legend()

        parameters = UList(ufloats=[UFloat(value, params_err[index]) for index, value in enumerate(params)])
        return parameters

    def add_legend(self, position: str, items_name, fit=False, subplot=None, **kwargs):
        if fit:
            items = [self.fit_lines.get(name)[0] for name in items_name]
        if not fit:
            items = [self.items.get(name) for name in items_name]

        # print(items[0])

        if subplot is not None:
            self.axs[subplot].add_artist(self.axs[subplot].legend(handles=items,loc=position,**kwargs))
        else:
            self.axs.add_artist(self.axs.legend(handles=items,loc=position,**kwargs))

        

    def move_legend(self, position: str, items_name=None, subplot=None, **kwargs):
        if subplot is not None:
            if items_name is not None:
                items = [self.items.get(name) for name in items_name]
                self.axs[subplot].legend(items,items_name,loc=position, **kwargs)
            else:
                self.axs[subplot].legend(loc=position, **kwargs)
        else:
            if items_name is not None:
                items = [self.items.get(name) for name in items_name]
                self.axs.legend(items,loc=position,**kwargs)
            else:
                self.axs.legend(loc=position,**kwargs)

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
        self.set_xlabel(x_label,subplot)
        self.set_ylabel(y_label,subplot)
       

    def set_xscale(self,scale: str, subplot=None):
        if subplot is not None:
            self.axs[subplot].set_xscale(scale)
        else:
            self.axs.set_xscale(scale)

    def set_yscale(self, scale:str, subplot=None):
        if subplot is not None:
            self.axs[subplot].set_yscale(scale)
        else:
            self.axs.set_yscale(scale)

    def set_scales(self,x_scale,y_scale,subplot=None):
        self.set_xscale(x_scale, subplot)
        self.set_yscale(y_scale, subplot)

    def set_xlim(self,xmin,xmax,subplot=None):
        if subplot is not None:
            self.axs[subplot].set_xlim(xmin, xmax)        
        else:
            self.axs.set_xlim(xmin, xmax)

    def set_ylim(self,ymin,ymax,subplot=None):
        if subplot is not None:
            self.axs[subplot].set_ylim(ymin, ymax)
        else:
            self.axs.set_ylim(ymin, ymax)

    def set_lims(self, xmin, xmax, ymin, ymax, subplot=None):
        self.set_xlim(xmin, xmax, subplot)
        self.set_ylim(ymin, ymax, subplot)
        

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
            self.axs[subplot].scatter(x,y,label=name,ms=self.marker_size,**kwargs)
        else:
            self.axs.scatter(x,y,label=name,ms=self.marker_size,**kwargs)

    def add_ufloat(self, other_val, ufloat, name, orientation: str, subplot=None, **kwargs):
        if subplot is not None:
            if orientation == 'y':
                self.axs[subplot].errorbar(other_val, ufloat._value, yerr=ufloat._error,label=name,ms=self.marker_size,fmt='.', **kwargs)
            if orientation == 'x':
                self.axs[subplot].errorbar(ufloat._value, other_val, xerr=ufloat._error,label=name,ms=self.marker_size,fmt='.',**kwargs)
        else:
            if orientation == 'y':
                self.axs.errorbar(other_val, ufloat._value, yerr=ufloat._error,label=name,ms=self.marker_size,fmt='.', **kwargs)
            if orientation == 'x':
                self.axs.errorbar(ufloat._value, other_val, xerr=ufloat._error,label=name,ms=self.marker_size,fmt='.',**kwargs)

    def add_ufloats(self, x_values: UList, y_values: UList, name: str, subplot=None, **kwargs):
        x, xerr = x_values.get_data()
        y, yerr = y_values.get_data()
        if subplot is not None:
            self.items[name] = self.axs[subplot].errorbar(x,y,yerr=yerr,xerr=xerr,fmt='.',ms=self.marker_size,label=name,**kwargs)
            self.lines_number[name] = self.number
            self.lines_data[name] = [x_values, y_values]
        else:
            self.lines[name] = self.axs.errorbar(x,y,yerr=yerr,xerr=xerr,fmt='.',ms=self.marker_size,label=name,**kwargs)
            self.lines_number[name] = self.number
            self.lines_data[name] = [x_values, y_values]
        
        self.number += 1

    def plot(self, x, y, name, subplot=None, **kwargs):
        if subplot is not None:
            self.axs[subplot].plot(x,y,label=name,ms=self.marker_size,**kwargs)
        else:
            self.axs.plot(x,y,label=name,ms=self.marker_size,**kwargs)


    def clear(self):
        self.axs.cla()

    def close(self):
        plt.close()
        
    def show(self):
        plt.show(block=True)


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
            sum_yerr = sum(y_err)
            if sum_yerr == 0:
                self.items[name] = self.axs[subplot].errorbar(x,y,xerr=x_err,label=name,**kwargs)
            else:
                self.items[name] = self.axs[subplot].errorbar(x,y,yerr=y_err,xerr=x_err,label=name,**kwargs)
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
            self.items[name] = self.axs.errorbar(x,y,yerr=y_err,xerr=x_err,label=name,**kwargs)
            self.axs.set_xlabel(xlabel)
            self.axs.set_ylabel(ylabel)
            self.axs.set_title(title)
            self.lines_number[name] = self.number
            self.lines_data[name] = [xdata,ydata]
        
        self.number += 1


class UHist(UPlot):
    def __init__(self, subplots=None, mosaic=False,share_x=False,share_y=False):
        super().__init__(subplots,mosaic,share_x,share_y)

    def add_hist(self, data: UList, bins: int, range: tuple, name: str, xlabel: str, ylabel: str, title: str, y_err: int, subplot=None, **kwargs):
        # x_values = []
        # y_values = []
        # for i in np.linspace(range[0],range[1],bins):
        #     y_values.append(data.get_values().count(i))
        #     x_values.append(int(i))
        #     # print(i)
        if range is not None:
            hist = np.histogram(data.get_values(),bins=bins-1, range=range)
        else:
            hist = np.histogram(data.get_values(),bins=bins-1)
        np_data = list(hist[0])
        missing_bin = data.get_values().count(hist[1][-1])
        np_data[-1] -= missing_bin
        np_data.append(missing_bin)
        
        x_values = hist[1]
        # print(x_values)
        y_values = np_data

        if subplot is not None:
            self.items[name] = self.axs[subplot].bar(x_values,y_values,label=name,fill=True,**kwargs)
            self.items[f"{name} Data"] = self.axs[subplot].errorbar(x_values,y_values,yerr=y_err,label=f"{name} Data",ecolor='black',fmt='.',ms=self.marker_size)
            self.axs[subplot].set_xlabel(xlabel)
            self.axs[subplot].set_ylabel(ylabel)
            self.axs[subplot].set_title(title)
            # self.set_xlim(min(x_values),max(x_values),subplot)
            self.lines_number[name] = self.number
            self.lines_data[name] = [UList(values=list(x_values),errors=0),UList(values=list(y_values),errors=1)]
        else:
            self.items[name] = self.axs.bar(x_values,y_values,label=f"{name} Histogram",fill=True,**kwargs)
            self.items[f"{name} Data"] = self.axs.errorbar(x_values,y_values,yerr=y_err,label=f"{name} Data",ecolor='black',fmt='.',ms=self.marker_size)
            self.axs.set_xlabel(xlabel)
            self.axs.set_ylabel(ylabel)
            self.axs.set_title(title)
            self.lines_number[name] = self.number
            self.lines_data[name] = [UList(values=list(x_values),errors=0),UList(values=list(y_values),errors=1)]
        
        self.number += 1

    def add_stacked_hist(self, x_values, y_values, name: str, xlabel: str, ylabel: str, title: str, subplot=None, **kwargs):
        # print(len(x_values),len(y_values))
        if subplot is not None:
            self.items[name] = self.axs[subplot].bar(x_values,y_values,label=name,fill=True,**kwargs)
            # self.lines[name] = self.axs[subplot].errorbar(x_values,y_values,yerr=y_err,label=f"{name} Data",ecolor='black',fmt='.',ms=self.marker_size)
            self.axs[subplot].set_xlabel(xlabel)
            self.axs[subplot].set_ylabel(ylabel)
            self.axs[subplot].set_title(title)
            # self.set_xlim(min(x_values),max(x_values),subplot)
            self.lines_number[name] = self.number
            self.lines_data[name] = [UList(values=list(x_values),errors=0),UList(values=list(y_values),errors=1)]
        else:
            self.items[name] = self.axs.bar(x_values,y_values,label=name,fill=True,**kwargs)
            # self.lines[name] = self.axs.errorbar(x_values,y_values,yerr=y_err,label=f"{name} Data",ecolor='black',fmt='.',ms=self.marker_size)
            self.axs.set_xlabel(xlabel)
            self.axs.set_ylabel(ylabel)
            self.axs.set_title(title)
            self.lines_number[name] = self.number
            self.lines_data[name] = [UList(values=list(x_values),errors=0),UList(values=list(y_values),errors=1)]
        
        self.number += 1

    

if __name__ == "__main__":
    c = UFloat(5, 0.05)
    d = UFloat(4,0.5)
    a = UFloat(3, 2)
    b = UFloat(10, 1)
    # b = UFloat(6.26e-34,0.01e-34)
    # a = UFloat(6.26e8, 0.01e6)
    # print(a)
    # print(b)
    list_ = UList(ufloats=[c,d])
    t2 = UList(ufloats=[a,b])
    list_ **= t2
    print(list_)
    # print(list_.to_latex('1', 1, 3, 'vertical', ['Data'], 'Balbal'))