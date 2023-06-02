#include "funcs.hpp"
#include "C:\Users\chloe\AppData\Local\Programs\Python\Python311\Lib\site-packages\pybind11\include\pybind11\pybind11.h"

namespace py = pybind11;

PYBIND11_MODULE(wrap, m){
    // m.def("test", &test);
    m.def("TOF", &TOF);
}

<%
cfg["sources"] = ["funcs.cpp"]
setup_pybind11(cfg)
%>