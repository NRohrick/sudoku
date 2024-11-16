//Author: Nathaniel Rohrick
//Date: 20200101
//Filename: sudoku.c
//Description: Solves sudoku puzzles utilizing binary backtracking algorithm.

#include "stdio.h"
//#include "stdin.h"
#include "string.h"

#define SECTORS 9
#define ELEMENTS 81

#define MASK  0b111111111

#define ONE   0b000000001 //1
#define TWO   0b000000010 //2
#define THREE 0b000000100 //4
#define FOUR  0b000001000 //8
#define FIVE  0b000010000 //16
#define SIX   0b000100000 //32
#define SEVEN 0b001000000 //64
#define EIGHT 0b010000000 //128
#define NINE  0b100000000 //256

static const unsigned int validNums[SECTORS] = { ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE };

typedef struct
{
    unsigned int row;
    unsigned int col;
    unsigned int sqr;
} Location;

typedef struct
{
    Location location;
    unsigned int initVal;
    unsigned int choices;
} Cell;

typedef struct
{
    unsigned int ranked[ELEMENTS];
    unsigned int rankedLen;
    unsigned int row[SECTORS];
    unsigned int col[SECTORS];
    unsigned int sqr[SECTORS];
    Cell cell[ELEMENTS];
} Puzzle;

static int const sqrPath[SECTORS][SECTORS] =
{
    {  0,  1,  2,  9, 10, 11, 18, 19, 20 },
    {  3,  4,  5, 12, 13, 14, 21, 22, 23 },
    {  6,  7,  8, 15, 16, 17, 24, 25, 26 },
    { 27, 28, 29, 36, 37, 38, 45, 46, 47 },
    { 30, 31, 32, 39, 40, 41, 48, 49, 50 },
    { 33, 34, 35, 42, 43, 44, 51, 52, 53 },
    { 54, 55, 56, 63, 64, 65, 72, 73, 74 },
    { 57, 58, 59, 66, 67, 68, 75, 76, 77 },
    { 60, 61, 62, 69, 70, 71, 78, 79, 80 },
};

int rowPath[SECTORS][SECTORS] =
{
    {  0,  1,  2,  3,  4,  5,  6,  7,  8 },
    {  9, 10, 11, 12, 13, 14, 15, 16, 17 },
    { 18, 19, 20, 21, 22, 23, 24, 25, 26 },
    { 27, 28, 29, 30, 31, 32, 33, 34, 35 },
    { 36, 37, 38, 39, 40, 41, 42, 43, 44 },
    { 45, 46, 47, 48, 49, 50, 51, 52, 53 },
    { 54, 55, 56, 57, 58, 59, 60, 61, 62 },
    { 63, 64, 65, 66, 67, 68, 69, 70, 71 },
    { 72, 73, 74, 75, 76, 77, 78, 79, 80 },
};

static const int colPath[SECTORS][SECTORS] =
{
    {  0,  9, 18, 27, 36, 45, 54, 63, 72 },
    {  1, 10, 19, 28, 37, 46, 55, 64, 73 },
    {  2, 11, 20, 29, 38, 47, 56, 65, 74 },
    {  3, 12, 21, 30, 39, 48, 57, 66, 75 },
    {  4, 13, 22, 31, 40, 49, 58, 67, 76 },
    {  5, 14, 23, 32, 41, 50, 59, 68, 77 },
    {  6, 15, 24, 33, 42, 51, 60, 69, 78 },
    {  7, 16, 25, 34, 43, 52, 61, 70, 79 },
    {  8, 17, 26, 35, 44, 53, 62, 71, 80 },
};

char numDecode(unsigned int num)
{
    switch(num)
    {
        case ONE :
            return '1';
        case TWO :
            return '2';
        case THREE :
            return '3';
        case FOUR :
            return '4';
        case FIVE :
            return '5';
        case SIX :
            return '6';
        case SEVEN :
            return '7';
        case EIGHT :
            return '8';
        case NINE :
            return '9';
        default :
            return '0';
    }
}

void populateSectors(Puzzle* puzzle)
{
    int i, j;
    for ( i = 0 ; i < SECTORS ; i++ )
    {
        for ( j = 0 ; j < SECTORS ; j++ )
        {
            puzzle->row[i] |= puzzle->cell[rowPath[i][j]].initVal;
            puzzle->col[i] |= puzzle->cell[colPath[i][j]].initVal;
            puzzle->sqr[i] |= puzzle->cell[sqrPath[i][j]].initVal;
        }
    }
}

unsigned int findRow(unsigned int n)
{
    return (n / 9);
}

unsigned int findCol(unsigned int n)
{
    return (n % 9);
}

unsigned int findSqr(unsigned int row, unsigned int col)
{
    if ( row < 3 )
    {
        if ( col < 3 ) return 0;
        else if ( col < 6 ) return 1;
        else return 2;
    }
    else if ( row < 6 )
    {
        if ( col < 3 ) return 3;
        else if ( col < 6 ) return 4;
        else return 5;

    }
    else
    {
        if ( col < 3 ) return 6;
        else if ( col < 6 ) return 7;
        else return 8;
    }
}

void findLocation(Location* location, const int n)
{
    location->row = findRow(n);
    location->col = findCol(n);
    location->sqr = findSqr(location->row, location->col);
    return;
}

void initPuzzle(char* path, Puzzle* puzzle)
{
    int i;
    FILE* fp;

    puzzle->rankedLen = 0;
    for ( i = 0 ; i < SECTORS ; i++ )
    {
            puzzle->row[i] = 0;
            puzzle->col[i] = 0;
            puzzle->sqr[i] = 0;
    }

    fp = fopen(path, "r");
    if (fp == NULL)
    {
        printf("Invalid format!");
        return;
    }
    int m = 0;
    for(i = 0; i < SECTORS; i++)
    {
        char buf[16];
        int n;
        fgets(buf, 16, fp);
        for(n = 0; n < SECTORS; n++)
        {
            puzzle->cell[m].initVal = (int)(buf[n] - '0');
            if ( puzzle->cell[m].initVal != 0 )
            {
                puzzle->cell[m].initVal = 0b1 << (puzzle->cell[m].initVal-1);
            }
            else
            {
                puzzle->ranked[puzzle->rankedLen] = m;
                puzzle->rankedLen++;
            }
            findLocation(&puzzle->cell[m].location, m);
            //printf("%d ", puzzle->cell[m].initVal);
            m++;
        }
        //printf("\n");
    }
    populateSectors(puzzle);
    //fclose(fp);
    return;
}
int solve(int i, Puzzle* puzzle)
{
    if ( i == puzzle->rankedLen )
    {
        exit(0);
        int q, p, w;
        //printf("")
        for ( q = 0, w = 0 ; q < SECTORS ; q++ )
        {
            for ( p = 0 ; p < SECTORS ; p++ )
            {
                printf("%c", numDecode(puzzle->cell[p].initVal));
            }
            printf("\n");
        }
        exit(0);
    }
    puzzle->cell[puzzle->ranked[i]].choices = puzzle->row[puzzle->cell[puzzle->ranked[i]].location.row] |
        puzzle->col[puzzle->cell[puzzle->ranked[i]].location.col] |
        puzzle->sqr[puzzle->cell[puzzle->ranked[i]].location.sqr];
    if ( puzzle->cell[puzzle->ranked[i]].choices == MASK )
        return 0;

    int j;
    for ( j = 0 ; j < SECTORS ; j++ )
    {
        if ( puzzle->cell[puzzle->ranked[i]].choices & (0b1 << j) )
            continue;
        else
        {
            //self.cell[self.ranked[index]].init_val = VALID_NUMS[i]#Select choice
            puzzle->cell[puzzle->ranked[i]].initVal = validNums[j];
            //Eliminate options from affected sectors.
            puzzle->row[puzzle->cell[puzzle->ranked[i]].location.row] |= puzzle->cell[puzzle->ranked[i]].initVal;
            puzzle->col[puzzle->cell[puzzle->ranked[i]].location.col] |= puzzle->cell[puzzle->ranked[i]].initVal;
            puzzle->sqr[puzzle->cell[puzzle->ranked[i]].location.sqr] |= puzzle->cell[puzzle->ranked[i]].initVal;
            //Solve next cell
            //if ( solve(i+1, puzzle) == -1 )
                //return -1;
            solve(i + 1, puzzle);
            //Dead end branch, clear selection and move on
            puzzle->row[puzzle->cell[puzzle->ranked[i]].location.row] &= (puzzle->cell[puzzle->ranked[i]].initVal ^ MASK);
            puzzle->col[puzzle->cell[puzzle->ranked[i]].location.col] &= (puzzle->cell[puzzle->ranked[i]].initVal ^ MASK);
            puzzle->sqr[puzzle->cell[puzzle->ranked[i]].location.sqr] &= (puzzle->cell[puzzle->ranked[i]].initVal ^ MASK);

            puzzle->cell[puzzle->ranked[i]].initVal = 0;
        }
    }
    return 0;
}

int main(int argc, char** argv)
{
    Puzzle puzzle;
    printf("%s\n", argv[argc-1]);

    initPuzzle(argv[argc-1], &puzzle);
    if ( solve(0, &puzzle) == -1 )
    {
        //printf("Solution Found !\n");
    }
    else
    {
        printf("Solution Not Found ! \n");
        //return 0;
    }
    int i, j, m;
    for ( i = 0, m = 0 ; i < SECTORS ; i++ )
    {
        for ( j = 0 ; j < SECTORS ; j++ )
        {
            printf("%c", numDecode(puzzle.cell[m].initVal));
            m++;
        }
        printf("\n");
    }
    return 0;
}
