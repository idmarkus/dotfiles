#ifndef VERUS_TYPEDEFS_H
#define VERUS_TYPEDEFS_H

#include <stdint.h>

/* General */
typedef uint_fast8_t  u8;
typedef uint_fast16_t u16;
typedef uint_fast32_t u32;
typedef uint_fast64_t u64;

typedef int_fast8_t  i8;
typedef int_fast16_t i16;
typedef int_fast32_t i32;
typedef int_fast64_t i64;

/* Exact sizes */
typedef uint8_t  u8_t;
typedef uint16_t u16_t;
typedef uint32_t u32_t;
typedef uint64_t u64_t;

/*
#define 1u8  ((u8_t)(1ull))
#define 1u16 ((u16_t)(1ull))
#define 1u32 ((u32_t)(1ull))
#define 1u64 ((u64_t)(1ull))
*/

// Note: Are cast-macros really necessary?
#define u8(x)  ((u8_t)(x))
#define u16(x) ((u16_t)(x))
#define u32(x) ((u32_t)(x))
#define u64(x) ((u64_t)(x))

typedef int8_t  i8_t;
typedef int16_t i16_t;
typedef int32_t i32_t;
typedef int64_t i64_t;

/* Smallest type with at least N bits */
typedef uint_least8_t  u8_least;
typedef uint_least16_t u16_least;
typedef uint_least32_t u32_least;
typedef uint_least64_t u64_least;

typedef int_least8_t  i8_least;
typedef int_least16_t i16_least;
typedef int_least32_t i32_least;
typedef int_least64_t i64_least;

/* Maximums */
typedef intmax_t  imax_t;
typedef uintmax_t umax_t;

/* Pointer types */
typedef intptr_t  iptr_t;
typedef uintptr_t uptr_t;


/* Floats */
typedef float f32;
typedef double f64;



/* New styles */
typedef unsigned int N;
typedef int          Z;
typedef double        R;

typedef uint8_t      N8_t;
typedef uint16_t     N16_t;
typedef uint32_t     N32_t;
typedef uint64_t     N64_t;

typedef int8_t      Z8_t;
typedef int16_t     Z16_t;
typedef int32_t     Z32_t;
typedef int64_t     Z64_t;
#endif // VERUS_TYPEDEFS_H
