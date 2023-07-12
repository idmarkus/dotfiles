#pragma once
#include <verus/typedefs.h>
#include "isprime.h"
#include <iostream>

//template <typename T>
bool isDivisible(u32 n)
{
    if (n == 1)
    {
        return false;
    }
    else if (n == 2)
    {
        return true;
    }
    else
    {
        return !isprime(n);
    }
}

template <class T>
struct ratio
{
    T numerator;
    T denominator;
    bool is_unit()
    {
        if (this->denominator % this->numerator == 0)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    void simplify() {
        // Check if the numerator is a proper divisor of the denominator.
        // If it is, return 1 / (denominator divided by numerator).
        if (this->denominator % this->numerator == 0)
        {
            this->denominator = this->denominator / this->numerator;
            this->numerator = 1;
            return;
        }
    
        // While both the numerator and denominator are not prime:
        while (isDivisible(this->numerator) && isDivisible(this->denominator)) {
            // Check all whole numbers from 2 to (numerator - 1),
            // If a common divisor is found, divide both
            // numerator and denominator and repeat.
            bool found_divisor = false;
            for (uint i = 2; i < this->numerator; i++)
            {
                if (this->numerator % i == 0 && this->denominator % i == 0)
                {
                    found_divisor = true;
                    this->numerator   /= i;
                    this->denominator /= i;
                }
            }
            // If a common divisor wasn't found,
            // (the ratio is already in lowest common terms)
            // break to return it.
            if (!found_divisor)
            {
                break;
            }
        }
    }
    ratio<T> operator+(ratio<T> b)
    {
        ratio<T> n = {this->numerator, this->denominator};
        n.numerator = (this->numerator * b.denominator) + (b.numerator * this->denominator);
        n.denominator = this->denominator * b.denominator;
        return n;
    }
    ratio<T> operator*(ratio<T> b)
    {
        ratio<T> n = {this->numerator, this->denominator};
        n.numerator *= b.numerator;
        n.denominator *= b.denominator;
        return n;
    }
    ratio<T> operator/(ratio<T> b)
    {
        ratio<T> n = {this->numerator, this->denominator};
        n.numerator *= b.denominator;
        n.denominator *= b.numerator;
        return n;
    }
    ratio<T> operator-(ratio<T> b)
    {
        uint new_num = (this->numerator * b.denominator) - (b.numerator * this->denominator);
        uint new_denom = (this->denominator * b.denominator);
        ratio<T> new_f = {new_num, new_denom};
        return new_f;
    }
    void operator+=(ratio<T> b)
    {
        this->numerator = (this->numerator * b.denominator) + (b.numerator * this->denominator);
        this->denominator = this->denominator * b.denominator;
    }
    void operator*=(ratio<T> b)
    {
        this->numerator *= b.numerator;
        this->denominator *= b.denominator;
    }
    void operator/=(ratio<T> b)
    {
        this->numerator *= b.denominator;
        this->denominator *= b.numerator;
    }
    bool operator==(ratio<T> b)
    {
        this->simplify();
        b.simplify();
        if (this->numerator == b.numerator && this->denominator == b.denominator)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
};

template <typename T>
std::ostream& operator<<(std::ostream& os, const ratio<T>& f)
{
    return os << f.numerator << "÷" << f.denominator;
}
