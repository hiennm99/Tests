from typing import List
import numpy as np
from fastapi import HTTPException


def cal_percentile(data: List[float], k: float):
    if k > 100:
        raise HTTPException(
            status_code=400,
            detail="k must be between 0 and 100")
    
    n = len(data)
    data = sorted(data)
    
    if n == 0:
        raise HTTPException(
            status_code=400,
            detail="Pool values must not be empty.")
    elif (0 < n < 100):
        i = (k / 100) * (n - 1)
        j = int(i)

        if (j + 1 >= n):
            return (data[j], n)
        
        p = data[j] + (i - j) * (data[j + 1] - data[j])
        return (p, n)
    else:
        p = np.percentile(data, k)
        return (p, n)