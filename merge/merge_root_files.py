# import typing
import uproot
import numpy as np

from dataclasses import dataclass
from pathlib import Path
from bytechomp.datatypes import U16, U64



def uint64_diff(a: U64, b: U64) -> tuple[U64, int]:
    if a == b:
        return 0, 0
    elif a > b:
        return a - b, 1
    else:
        return b - a, -1
    
    
@dataclass
class ConsolidatedData:
    timestamp0: U64
    timestamp1: U64
    energy0: U16
    energy1: U16

class Merger:
    """
    
    """
    def __init__(self, file_ch0: Path, file_ch1: Path) -> None:
        self.file_ch0__: Path = file_ch0
        self.file_ch1__: Path = file_ch1
        
    def merge(self) -> None:     
        root_file0 = uproot.open(self.file_ch0__)
        root_file1 = uproot.open(self.file_ch1__)

        tree0 = root_file0["Data_R"]
        tree1 = root_file1["Data_R"]
        
        keys = ['Timestamp', 'Energy']
        filtered_data0 = tree0.arrays(keys, library='np')
        filtered_data1 = tree1.arrays(keys, library='np')
       
        root_file0.close()
        root_file1.close()
        
        # idx0: int = 0
        # idx1: int = 0
        # idx_max0: int = len(filtered_data0['Timestamp']) 
        # idx_max1: int = len(filtered_data1['Timestamp']) 
        # print(filtered_data0["Timestamp"])         
        # print(filtered_data1["Timestamp"]) 
               
        result: list[ConsolidatedData] = []
        
        delta: U64
        threshold: U64= 0
        iter_t0 = np.nditer(filtered_data0["Timestamp"])
        iter_e0 = np.nditer(filtered_data0["Energy"])
        iter_t1 = np.nditer(filtered_data1["Timestamp"])
        iter_e1 = np.nditer(filtered_data1["Energy"])
       
        t0 = next(iter_t0)
        e0 = next(iter_e0)
        t1 = next(iter_t1) 
        e1 = next(iter_e1)
        while t0 != 0 and t1 != 0:
            delta, sign = uint64_diff(t0, t1)
            if delta <= threshold:
                result.append(ConsolidatedData(t0, t1, e0, e1))
                
                t0 = next(iter_t0, 0)
                e0 = next(iter_e0, 0)
                
                t1 = next(iter_t1, 0) 
                e1 = next(iter_e1, 0)
            elif sign < 0:
                t0 = next(iter_t0, 0)
                e0 = next(iter_e0, 0)
            elif sign > 0:
                t1 = next(iter_t1, 0) 
                e1 = next(iter_e1, 0)
                
        print("result len:", len(result)) 
                
if __name__ == '__main__':
    toto: Merger = Merger(Path("./data/DataR_CH0@DT5751_1989_Co60-EQ2611-20-CFD.root"), Path("./data/DataR_CH1@DT5751_1989_Co60-EQ2611-20-CFD.root"))
    
    toto.merge()