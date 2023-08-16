//Start of config
#include "C:/Users/chloe/AppData/Local/Programs/Python/Python311/include/Python.h"
#include "C:/Users/chloe/AppData/Local/Programs/Python/Python311/Lib/site-packages/pybind11/include/pybind11/numpy.h"
#include "C:/Users/chloe/AppData/Local/Programs/Python/Python311/Lib/site-packages/pybind11/include/pybind11/pybind11.h"
//End of config
#include <vector>
#include <tuple>
#include <string>
#include <iostream>

namespace py = pybind11;

// Function to switch from vector to py_array form. The vector form will be mostly used by C++ and the py_array is the Python format.

#define NEW_VERSION 1
#if NEW_VERSION 
/**Transform a Python array containing one data type to a vector containing the same data type.*/
template<class T> std::vector<T> ARRAY_TO_VEC(const py::array_t<T> & array);
/**Transforms a C++ vector containing one data type to a Python array containing the same data type*/
template<class T> py::array_t<T> VEC_TO_ARRAY(const std::vector<T> & vec);

#else 
/**Transform a Python array containing int64_t to a vector containing int64_t.*/
std::vector<int64_t> ARRAY_TO_VEC(py::array_t<int64_t> array);
/**Transform a Python array containing unsigned long long to a vector containing unsigned long long.*/
std::vector<unsigned long long> ARRAY_TO_VEC(py::array_t<unsigned long long> array);

/**Transforms a C++ vector containing int64_t to a Python array containing int64_t*/
py::array_t<int64_t> VEC_TO_ARRAY(std::vector<int64_t> vec);
/**Transforms a C++ vector containing unsinged long long to a Python array containing unsigned long long*/
py::array_t<unsigned long long> VEC_TO_ARRAY(std::vector<unsigned long long> vec);
#endif

// Mathematical functions on vectors
std::vector<int64_t> substract_abs(const std::vector<int64_t> & vec, int64_t value);

// This function runs the TOF analysis on all cores of the machine.
std::tuple<py::array_t<int64_t>, py::array_t<int64_t>> TOF(py::array_t<int64_t> array_start, py::array_t<int64_t> array_stop, int64_t window);

// Test function for the wrapper
// std::tuple<py::array_t<int64_t>, py::array_t<unsigned long long>> test(py::array_t<int64_t> test_array);

