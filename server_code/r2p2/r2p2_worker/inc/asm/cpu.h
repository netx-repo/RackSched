#pragma once

/*
 * Endianness
 */

#define __LITTLE_ENDIAN 1234
#define __BIG_ENDIAN    4321

#define __BYTE_ORDER    __LITTLE_ENDIAN


/*
 * Word Size
 */

#define __32BIT_WORDS   32
#define __64BIT_WORDS   64

#define __WORD_SIZE __32BIT_WORDS

#define CACHE_LINE_SIZE 64
