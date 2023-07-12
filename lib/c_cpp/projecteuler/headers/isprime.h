#pragma once 
#include <verus/typedefs.h>
#include "dbg.hpp"

#ifndef __cplusplus
#include <stdbool.h>
bool isprime(u32 n) {
    if (n == 1 || n == 0)
        return false;
    else if (n <= 3)
        return true;
    else if (n % 2 == 0 || n % 3 == 0)
        return false;
    else {
        for (u32 i = 5; i*i <= n; i+= 2) {
            if (n % i == 0)
                return false;
        }
        return true;
    }
}
#else
#include <personal/dbg.hpp>

template <typename T>
bool isprime(T n)
{
    benchmark_fn();
    if (n == 1 || n == 0)
        return false;
    else if (n <= 3)
        return true;
    else if (n % 2 == 0 || n % 3 == 0)
        return false;
    else {
        for (u32 i = 5; i*i <= n; i+= 2) {
            if (n % i == 0)
                return false;
        }
        return true;
    }
}


#endif
