#pragma once
#include <personal/typedefs.h>
#include <personal/dbg.hpp>

/** isprime()
 */
namespace isprime_helpers
{
    int64_t power(int a, int n, int mod)
    {
        int64_t power = a, result = 1;

        while(n)
        {
            if(n & 1) 
                result = (result * power) % mod;
            power = (power * power) % mod;
            n >>= 1;
        }
        return result;
    }

    bool witness(int a, int n)
    {
        int t,u,i;
        int64_t prev,curr;

        u=n/2;
        t=1;
        while(!(u&1))
        {
            u/=2;
            ++t;
        }

        prev=power(a,u,n);
        for(i=1;i<=t;++i)
        {
            curr=(prev*prev)%n;
            if((curr==1)&&(prev!=1)&&(prev!=n-1)) 
                return true;
            prev=curr;
        }
        if(curr!=1) 
            return true;
        return false;
    }
}
inline bool isprime( int number )
{
    benchmark_fn();
    using namespace isprime_helpers;
    
    if ( ( (!(number & 1)) && number != 2 ) || (number < 2) || (number % 3 == 0 && number != 3) )
        return (false);

    if(number<1373653)
    {
        for( int k = 1; 36*k*k-12*k < number;++k)
            if ( (number % (6*k+1) == 0) || (number % (6*k-1) == 0) )
                return (false);

        return true;
    }

    if(number < 9080191)
    {
        if(witness(31,number)) return false;
        if(witness(73,number)) return false;
        return true;
    }


    if(witness(2,number)) return false;
    if(witness(7,number)) return false;
    if(witness(61,number)) return false;
    return true;

    /*WARNING: Algorithm deterministic only for numbers < 4,759,123,141 (unsigned int's max is 4294967296)
      if n < 1,373,653, it is enough to test a = 2 and 3.
      if n < 9,080,191, it is enough to test a = 31 and 73.
      if n < 4,759,123,141, it is enough to test a = 2, 7, and 61.
      if n < 2,152,302,898,747, it is enough to test a = 2, 3, 5, 7, and 11.
      if n < 3,474,749,660,383, it is enough to test a = 2, 3, 5, 7, 11, and 13.
      if n < 341,550,071,728,321, it is enough to test a = 2, 3, 5, 7, 11, 13, and 17.*/
}

/** iscoprime(a, b)
 */
bool iscoprime(N64_t a, N64_t b)
{
    benchmark_fn();
         if (a == b)                   return false;
    else if (a == 0 || b == 0)         return false;
    else if (a == 1 || b == 1)         return true;
    else if (a % b == 0 || b % a == 0) return false;

         //static vector<N64_t> primes;
         //if (primes.empty()) fillprimes(primes, LIM);
    
    const N64_t lowest  = (a < b) ? a : b;
    const N64_t highest = (a > b) ? a : b;
    for (N64_t f = 2; (f * f) <= lowest; ++ f)
    {
        if (lowest % f == 0)
        {
            if (highest % f == 0)
            {
                return false;
            }
            if (highest % (lowest / f) == 0/* && lowest != f */)
            {
                return false;
            }
        }
    }
    return true;
}

/** GCD()
 */
N GCD(N a, N b)
{
    benchmark_fn();
    for (N f = (a < b) ? a : b; f > 0; -- f)
    {
        if (a % f == 0 && b % f == 0)
        {
            return f;
        }
    }
    return 1;
}

/** fraction_gt(a_n, a_d, b_n, b_d)
 */
inline bool fraction_gt(N a_n, N a_d, N b_n, N b_d)
{
    benchmark_fn();
    return ((a_n * b_d) > (b_n * a_d));
}

/** fraction_gteq(a_n, a_d, b_n, b_d)
 */
inline bool fraction_gteq(N a_n, N a_d, N b_n, N b_d)
{
    benchmark_fn();
    return ((a_n * b_d) >= (b_n * a_d));
}


#include <vector>
std::vector<uint> factors_slow(uint n)
{
    if (isprime(n) || n == 1)
    {
        return {n};
    }
    
    std::vector<uint> result;

    uint p = 2;
    while (p*p <= n)
    {
        if (isprime(p) && n % p == 0)
        {            
            result.push_back(p);
            n /= p;
            p = 2;
        }
        else
        {
            ++ p;
        }
    }

    result.push_back(n);
    return result;
}
