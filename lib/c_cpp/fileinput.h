#ifndef VERUS_FILEINPUT_H
#define VERUS_FILEINPUT_H

#include <stdio.h>
#include <stdlib.h>

char * file_strbfr(FILE * f)
{
    size_t fsize = ftell(f);
    fseek(f, 0, SEEK_END);
    fsize = ftell(f) - fsize;
    rewind(f);

    char * bfr = (char *)malloc(sizeof(char) * fsize + 1);
    if (bfr == NULL)
    {
        fprintf(stderr, "file_strbfr: malloc failed\n");
        fclose(f);
        return NULL;
    }

    size_t rd_cnt = fread(bfr, 1, fsize, f);
    if (rd_cnt != fsize)
    {
        fprintf(stderr, "file_strbfr: fread: %lu expected, %lu read\n", fsize, rd_cnt);
    }

    fclose(f);
    return bfr;
}

char * input_strbfr(int argc, char ** argv)
{
    char * fstr = NULL;

    if (argc > 1) // assume argument[1] is a filename
    {
        FILE * f = fopen(argv[1], "r");
        if (f == NULL)
        {
            fprintf(stderr, "error: input_strbfr: fopen(%s (argv[1]), \"r\") failed\n", argv[1]);
            return NULL;
        }
        fstr = file_strbfr(f);
    }
    else // no arguments
    {
        fstr = file_strbfr(stdin);
    }

    return fstr;
}

#endif /* VERUS_FILEINPUT_H */
