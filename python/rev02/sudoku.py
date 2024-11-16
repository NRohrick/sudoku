import csv
import numpy as np
import time

ELEMENTS = 81
SECTORS = 9
VALID_NUMS = [ x+1 for x in range(SECTORS) ]

VALID_NUMS = [ 1 << x for x in range(SECTORS)]
VALID_NUMS.append(0)

ONE =	 0b000000001	#1
TWO =	 0b000000010	#2
THREE =	 0b000000100	#4
FOUR =	 0b000001000	#8
FIVE =   0b000010000	#16
SIX = 	 0b000100000	#32
SEVEN =  0b001000000	#64
EIGHT =  0b010000000	#128
NINE =   0b100000000	#256
MASK =   0b111111111

numDecode =\
{
	ONE:1,
	TWO:2,
	THREE:3,
	FOUR:4,
	FIVE:5,
	SIX:6,
	SEVEN:7,
	EIGHT:8,
	NINE:9
}

SQUARE_PATH = [
	[ 0,  1,  2,  9, 10, 11, 18, 19, 20],
	[ 3,  4,  5, 12, 13, 14, 21, 22, 23],
	[ 6,  7,  8, 15, 16, 17, 24, 25, 26],
	[27, 28, 29, 36, 37, 38, 45, 46, 47],
	[30, 31, 32, 39, 40, 41, 48, 49, 50],
	[33, 34, 35, 42, 43, 44, 51, 52, 53],
	[54, 55, 56, 63, 64, 65, 72, 73, 74],
	[57, 58, 59, 66, 67, 68, 75, 76, 77],
	[60, 61, 62, 69, 70, 71, 78, 79, 80]
]


ROW_PATH = [[] for i in range(SECTORS)]
for i in range(SECTORS):
	ROW_PATH[i] = list(range(i*SECTORS, (i+1)*SECTORS))

COL_PATH = [[] for i in range(SECTORS)]
for i in range(SECTORS):
	COL_PATH[i] = list(range(i, i+SECTORS*SECTORS, SECTORS))
print('colpath',COL_PATH)
print('rowpath',ROW_PATH)
print('valid',VALID_NUMS)
p = []
with open('puzzle.csv', 'r') as fp:
	reader = csv.reader(fp)
	puzzle = []
	for row in reader:
		row = [int(i) for i in row]
		p.append(row)
print(p)

#Finds the column number of given cell
def find_col(n):
	return (n % 9)

#Finds the row number of given cell
def find_row(n):
	return int(n / 9)

#Finds the square number of given cell
#TODO switch case statement to save CPU comparisons
def find_square(r, c):
	if r < 3:
		if c < 3:
			return 0
		elif c < 6:
			return 1
		else:
			return 2
	elif r < 6:
		if c < 3:
			return 3
		elif c < 6:
			return 4
		else:
			return 5
	else:
		if c < 3:
			return 6
		elif c < 6:
			return 7
		else:
			return 8

#Determines cell attributes
def find_location(n):
	r = find_row(n)
	c = find_col(n)
	s = find_square(r, c)
	return [r, c, s]

class Puzzle_Cell:
	def __init__(self, n, init_val):
		self.r = 0
		self.c = 0
		self.s = 0
		self.init_val = 0
		[self.r, self.c, self.s] = find_location(n)
		self.init_val = VALID_NUMS[init_val - 1]
		if init_val != 0:
			self.choices = VALID_NUMS[init_val - 1]
		else:
			self.choices = 0b111111111

class Puzzle:
	ranked = []
	ranked_len = []
	myPuzzle = []
	row = [ 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0 ]
	col = [ 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0 ]
	sqr = [ 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0 ]

	def __populate_row(self):
		for n in range(SECTORS):
			for i in ROW_PATH[n]:
				self.row[n] |= self.cell[i].init_val

	def __populate_col(self):
		for n in range(SECTORS):
			for i in COL_PATH[n]:
				self.col[n] |= self.cell[i].init_val

	def __populate_square(self):
		for n in range(SECTORS):
			for i in SQUARE_PATH[n]:
				self.sqr[n] |= self.cell[i].init_val

	def __solve(self, index):
		if index == (self.ranked_len):
			print('FINAL INDEX REACHED')
			return -1
		self.cell[self.ranked[index]].choices = self.row[self.cell[self.ranked[index]].r] | self.col[self.cell[self.ranked[index]].c] | self.sqr[self.cell[self.ranked[index]].s]
		if self.cell[self.ranked[index]].choices == MASK:
			return
		for i in range(SECTORS):
			if self.cell[self.ranked[index]].choices & (0b1 << i):
				continue
			else:
				self.cell[self.ranked[index]].init_val = VALID_NUMS[i]#Select choice
				#Eliminate options from affected sectors.
				self.row[self.cell[self.ranked[index]].r] |= self.cell[self.ranked[index]].init_val
				self.col[self.cell[self.ranked[index]].c] |= self.cell[self.ranked[index]].init_val
				self.sqr[self.cell[self.ranked[index]].s] |= self.cell[self.ranked[index]].init_val

				#Solve next cell
				if self.__solve(index+1) == -1:
					return -1
				#Dead end branch, clear selection and move on
				self.row[self.cell[self.ranked[index]].r] &= (self.cell[self.ranked[index]].init_val ^ MASK)
				self.col[self.cell[self.ranked[index]].c] &= (self.cell[self.ranked[index]].init_val ^ MASK)
				self.sqr[self.cell[self.ranked[index]].s] &= (self.cell[self.ranked[index]].init_val ^ MASK)
				self.cell[self.ranked[index]].init_val = 0
	def __init__(self):
		self.myPuzzle = [j for i in p for j in i]#Unfold puzzle into 1d array

		#Initialize all cell values
		self.cell = [Puzzle_Cell(n, self.myPuzzle[n]) for n in range(ELEMENTS)]

		self.__populate_col()
		self.__populate_row()
		self.__populate_square()
		for n in range(ELEMENTS):
			if self.cell[n].init_val == 0:
				self.ranked.append(n)

		self.ranked_len = len(self.ranked)
		self.__solve(0)

		solution = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		interim = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		for i in range(SECTORS):
			for n in range(SECTORS):
				interim[n] = numDecode[self.cell[i*9 + n].init_val]
			solution[i] = interim
			print(interim)

start_time = time.clock()
Puzzle = Puzzle()
print(time.clock() - start_time, "seconds")