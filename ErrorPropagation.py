import numpy as np

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
    def first_digit(value: float):
        value = list(f"{value:.20f}")
        to_remove = 0
        for index, digit in enumerate(value):
            if digit == '0':
                continue
            if digit =='.':
                to_remove = 1
            else:
                return index - to_remove

    def __str__(self):
        length = self.first_digit(self._error)
        return f"({self._value:.{length}f}±{self._error:.{length}f})"

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

    def __lt__(self, other):
        return self._value < other._value
    
    def __le__(self, other):
        return self._value <= other._value

    def __eq__(self, other):
        return self._value == other._value
    
    def __ne__(self, other):
        return self._value != other._value

    def __gt__(self, other):
        return self._value > other._value

    def __ge__(self, other):
        return self._value >= other._value

    def evalf(self, func: callable):
        value = func(self._value)
        error = np.sqrt((func(self._value+self._error) - value)**2)
        return UFloat(value, error)


if __name__ == "__main__":
    test = UFloat(0.45, 0.000005)
    test2 = UFloat(1.00, 0.01)
    print(test2*2)