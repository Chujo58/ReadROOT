#include "funcs.hpp"
//Start of config
#include "C:/Users/chloe/AppData/Local/Programs/Python/Python311/Lib/site-packages/pybind11/include/pybind11/pybind11.h"
//End of config

namespace py = pybind11;

PYBIND11_MODULE(wrap, m){
    // m.def("test", &test);
    m.def("TOF", &TOF);
}

