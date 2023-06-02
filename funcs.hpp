#include "C:/Users/chloe/AppData/Local/Programs/Python/Python311/include/Python.h"
#include "C:\Users\chloe\AppData\Local\Programs\Python\Python311\lib\site-packages\pybind11\include\pybind11\pybind11.h"
#include "C:\Users\chloe\AppData\Local\Programs\Python\Python311\lib\site-packages\pybind11\include\pybind11\numpy.h"
#include <vector>
#include <tuple>
#include <string>
#include <iostream>

namespace py = pybind11;

// Function to switch from vector to py_array form.
#define NEW_VERSION 1
#if NEW_VERSION 
template<class T> std::vector<T> ARRAY_TO_VEC(const py::array_t<T> & array);
template<class T> py::array_t<T> VEC_TO_ARRAY(const std::vector<T> & vec);

#else 
std::vector<int64_t> ARRAY_TO_VEC(py::array_t<int64_t> array);
std::vector<unsigned long long> ARRAY_TO_VEC(py::array_t<unsigned long long> array);

py::array_t<int64_t> VEC_TO_ARRAY(std::vector<int64_t> vec);
py::array_t<unsigned long long> VEC_TO_ARRAY(std::vector<unsigned long long> vec);
#endif
// Function to find the indexes of values in a range
std::vector<int64_t> get_values_in_range(const std::vector<int64_t> & vec, int64_t lower_bound, int64_t upper_bound);

// Mathematical functions on vectors
std::vector<int64_t> substract_abs(const std::vector<int64_t> & vec, int64_t value);

std::tuple<py::array_t<int64_t>, py::array_t<int64_t>> TOF(py::array_t<int64_t> array_start, py::array_t<int64_t> array_stop, int64_t window);

// Test function for the wrapper
// std::tuple<py::array_t<int64_t>, py::array_t<unsigned long long>> test(py::array_t<int64_t> test_array);

