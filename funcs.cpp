#include "funcs.hpp"

#include <algorithm>
#define MEASURE 1
#if MEASURE
#include <chrono>
#include <future>
#include <iostream>
#endif
// #include <thread>
#include <vector>

#if NEW_VERSION

template<class T>
std::vector<T> ARRAY_TO_VEC(const py::array_t<T> & array){
    std::vector<T> copy(array.size());
    std::memcpy(copy.data(), array.data(), array.size()*sizeof(T));
    return copy;
}

template<class T>
py::array_t<T> VEC_TO_ARRAY(const std::vector<T> & vec){
    py::array_t<T> result = py::array_t<T>(vec.size());
    auto buffer = result.request();
    T *result_ptr = (T *) buffer.ptr;
    std::memcpy(result_ptr, vec.data(), vec.size()*sizeof(T));
    return result;
}

#else

std::vector<int64_t> ARRAY_TO_VEC(py::array_t<int64_t> array){
    std::vector<int64_t> copy(array.size());
    std::memcpy(copy.data(), array.data(), array.size()*sizeof(int64_t));
    return copy;
}

std::vector<unsigned long long> ARRAY_TO_VEC(py::array_t<unsigned long long> array){
    std::vector<unsigned long long> copy(array.size());
    std::memcpy(copy.data(), array.data(), array.size()*sizeof(unsigned long long));
    return copy;
}

py::array_t<int64_t> VEC_TO_ARRAY(std::vector<int64_t> vec){
    auto result = py::array_t<int64_t>(vec.size());
    auto buffer = result.request();
    int64_t *result_ptr = (int64_t *) buffer.ptr;
    std::memcpy(result_ptr, vec.data(), vec.size()*sizeof(int64_t));
    return result;
}

py::array_t<unsigned long long> VEC_TO_ARRAY(std::vector<unsigned long long> vec){
    auto result = py::array_t<unsigned long long>(vec.size());
    auto buffer = result.request();
    unsigned long long *result_ptr = (unsigned long long *) buffer.ptr;
    std::memcpy(result_ptr, vec.data(), vec.size()*sizeof(unsigned long long));
    return result;
}
#endif

#define NEW_VERSION2 0

#if NEW_VERSION2
std::vector<unsigned long long> get_indexes(const std::vector<int64_t> & vec, int64_t lower_bound, int64_t upper_bound){
    std::vector<int64_t> ret_vec(vec);

    ret_vec.erase(std::remove_if(
                      ret_vec.begin(),
                      ret_vec.end(), 
                      [&](int64_t val){ return val < lower_bound || val > upper_bound; }),
                  ret_vec.end());

    return ret_vec;
}
#else
std::vector<unsigned long long> get_indexes(const std::vector<int64_t> & vec, int64_t start_value, int64_t stop_value){
    std::vector<unsigned long long> indexes(vec.size());
    size_t j = 0;
    for (size_t i = 0; i < vec.size(); i++){
        if ((start_value <= vec[i]) && (vec[i] <= stop_value)){
            indexes[j] = i;
            j++;
        }
    }
    std::vector<unsigned long long> final_indexes(j);
    size_t k = 0;
    for (size_t i = 0; i < indexes.size(); i++){
        if (indexes[i] != 0){
            final_indexes[k] = indexes[i];
            k++;
        }
    }
    return final_indexes;
}
#endif

#define new_version3 1
#if new_version3
std::vector<int64_t> substract_abs(const std::vector<int64_t> & vec, int64_t value){
    std::vector<int64_t> output;
    output.reserve(vec.size());

    std::transform(vec.cbegin(), vec.cend(), back_inserter(output), [&](int64_t val){
        return abs(val - value);
    });
    return output;
}
#else
std::vector<int64_t> substract_abs(std::vector<int64_t> vec, int64_t value){
    std::vector<int64_t> output(vec.size());
    for (size_t i = 0; i < vec.size(); i++){
        output[i] = abs(vec[i] - value);
    }
    return output;
}
#endif

std::pair<std::vector<int64_t>, std::vector<int64_t>> process( 
        const std::vector<int64_t> & starts, 
        const std::vector<int64_t> & stops, 
        int64_t upper_bound) {
    const std::size_t starts_size = starts.size();
    std::cout << "Processing slice: " << starts_size << std::endl;
    std::vector<int64_t> res_starts; // (starts_size);
    std::vector<int64_t> res_stops; // (starts_size);

    for (int64_t start_time: starts) {
        for (int64_t stop_time: stops) {
            if (abs(stop_time - start_time) <= upper_bound) {
                res_starts.push_back(start_time);
                res_stops.push_back(stop_time);
                break;
            }
        }
    }
    std::cout << res_starts.size() << std::endl;
    // for(int64_t d:res_starts) {
    //     std::cout << "qaz:" << d << std::endl;
    // }
    // start.erase(std::remove(start.begin(), start.end(), 0), start.end());
    // stop.erase(std::remove(stop.begin(), stop.end(), 0), stop.end());
    // return {res_starts, res_stops};
    return {res_starts, res_stops};
}

 

std::tuple<py::array_t<int64_t>, py::array_t<int64_t>> TOF(py::array_t<int64_t> array_start, py::array_t<int64_t> array_stop, int64_t upper_bound){
#if MEASURE
    auto tstart = std::chrono::steady_clock::now();
#endif
    std::vector<int64_t> vector_start = ARRAY_TO_VEC(array_start);
    std::vector<int64_t> vector_stop = ARRAY_TO_VEC(array_stop);
#if MEASURE
    auto tend = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed_seconds = tend - tstart;
    std::cout << "Elapsed time for vector initialization: " << elapsed_seconds.count() << "s.\n";
#endif
    std::vector<int64_t> start; 
    std::vector<int64_t> stop;

#if 1
    std::cout << "C++ start vector size: " << vector_start.size() << std::endl;
    std::cout << "C++ stop vector size: " << vector_stop.size() << std::endl;

    const std::size_t cpu_count = std::thread::hardware_concurrency();
    const std::size_t vector_start_size = vector_start.size();
    const std::size_t slice_size = std::max<std::size_t>(1, vector_start_size / cpu_count);
     
    std::vector<std::future<std::pair<std::vector<int64_t>, std::vector<int64_t>>>> futures;

    for(std::size_t i = 0 ; i < vector_start_size; i += slice_size) {
        auto it_s = std::next(vector_start.begin(), i);
        auto it_e = std::next(vector_start.begin(), std::min(i + slice_size, vector_start_size));
        futures.push_back(std::async(process, std::vector<int64_t>(it_s, it_e), vector_stop, upper_bound));
    }
    for(auto & f: futures) {
        auto p= f.get();

        start.insert(start.end(), p.first.begin(), p.first.end());
        stop.insert(stop.end(), p.second.begin(), p.second.end());
    }

    return {VEC_TO_ARRAY(start), VEC_TO_ARRAY(stop)};
#else
    size_t j = 0;
    for (size_t i = 0; i < vector_start.size(); i++){
        int64_t start_time = vector_start[i];
        auto diffs = substract_abs(vector_stop, start_time);
        auto indexes = get_indexes(diffs, 0.0, upper_bound);
        if (indexes.size() != 0){
            start[j] = start_time;
            stop[j] = vector_stop[indexes[0]];
            j++;
            // std::cout << j << std::endl;
        }
    }

    std::vector<int64_t> final_start(j);
    std::vector<int64_t> final_stop(j);
    size_t k = 0;
    for (size_t i = 0; i < start.size(); i++){
        if (start[i] != 0){
            final_start[k] = start[i];
            k++;
        }
    }
    k = 0;
    for (size_t i = 0; i < stop.size(); i++){
        if (stop[i] != 0){
            final_stop[k] = stop[i];
            k++;
        }
    }

    auto start_array = VEC_TO_ARRAY(final_start);
    auto stop_array = VEC_TO_ARRAY(final_stop);
    return {start_array, stop_array};
#endif
}



// std::tuple<py::array_t<int64_t>, py::array_t<unsigned long long>> test(py::array_t<int64_t> test_array){
//     std::vector<int64_t> index = get_indexes(ARRAY_TO_VEC(test_array), 2.0, 3.0);
    
//     auto index_array = VEC_TO_ARRAY(index);

//     return {test_array, index_array};
// }