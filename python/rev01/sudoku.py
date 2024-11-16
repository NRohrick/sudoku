import csv
import numpy as np

ELEMENTS = 81
SECTORS = 9
VALID_NUMS = [ x+1 for x in range(SECTORS) ]

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
		self.choices = []
		self.removed_choices = []
		self.choice_ptr = 0
		self.locked = False
		self.temp_lock = False
		[self.r, self.c, self.s] = find_location(n)
		self.init_val = init_val
		if init_val != 0:
			self.locked = True
			self.choices = [init_val]
		else:
			self.choices = VALID_NUMS.copy()


#class Puzzle_Row:
#	available = [i for i in range(SECTORS)]
#	def __init__(self, e):


#class Puzzle_Col:

#class Puzzle_Square:

class Puzzle:
	#cell = []
	row = []
	col = []
	ranked = []
	ranked_len = []
	square = []
	myPuzzle = []

	def __populate_col(self, n):
		for i in range(SECTORS):
			if self.cell[(i * 9) + self.cell[n].c].init_val != 0:
				try:
					self.cell[n].choices.remove(self.cell[(i * 9) + self.cell[n].c].init_val)
				except ValueError:
					pass	

	def __populate_row(self, n):
		for i in range(SECTORS):
			if self.cell[self.cell[n].r * 9 + i].init_val != 0:
				try:
					self.cell[n].choices.remove(self.cell[self.cell[n].r * 9 + i].init_val)
					if n == 2:
						print(self.cell[n].choices)
				except ValueError:
					pass

	def __populate_square(self, n):
		for i in range(SECTORS):
			#Iterate every cell in square
			if self.cell[SQUARE_PATH[self.cell[n].s][i]].init_val != 0:
				try:
					self.cell[n].choices.remove(self.cell[SQUARE_PATH[self.cell[n].s][i]].init_val)
				except ValueError:
					pass

	#TODO: Numbers previously solved will have length 0 which will throw error
#	def __remove_n_r(self, row, num, n):
#		for i in ROW_PATH[row]

	def __unlock_r(self, row):
		for i in ROW_PATH[row]:
			self.cell[i].temp_lock = False

	def __unlock_c(self, col):
		for i in COL_PATH[col]:
			self.cell[i].temp_lock = False

	def __unlock_s(self, sqr):
		for i in SQUARE_PATH[sqr]:
			self.cell[i].temp_lock = False

	def __remove_n_r(self, row, num, n):
		for i in ROW_PATH[row]:
			if self.cell[i].locked == True:
				continue

			if self.cell[i].temp_lock == False:
				self.cell[i].removed_choices.append(num)
				self.cell[i].temp_lock = True
			if num in self.cell[i].choices:
				self.cell[i].choices.remove(num)
			else:
				continue

			if len(self.cell[i].choices) == 0:
				for m in range(ROW_PATH[row].index(i)+1):
					if self.cell[ROW_PATH[row][m]].locked == True:
						continue
					#if len(self.cell[ROW_PATH[row][m]].removed_choices) == 0:
					#	continue
					#if num in self.cell[ROW_PATH[row][m]].removed_choices:
					self.cell[ROW_PATH[row][m]].temp_lock = False
					self.cell[ROW_PATH[row][m]].removed_choices.remove(num)
					if num in self.cell[ROW_PATH[row][m]].removed_choices:
						continue
					else:
						self.cell[ROW_PATH[row][m]].choices.append(num)

				return -1			
		return 0

	def __remove_n_c(self, col, num, n):
		for i in COL_PATH[col]:
			if self.cell[i].locked == True:
				continue					

			if self.cell[i].temp_lock == False:
				self.cell[i].removed_choices.append(num)
				self.cell[i].temp_lock = True
			if num in self.cell[i].choices:
				self.cell[i].choices.remove(num)
			else:
				continue

			if len(self.cell[i].choices) == 0:
				for m in range(COL_PATH[col].index(i)+1):
					if self.cell[COL_PATH[col][m]].locked == True:
						continue
					self.cell[COL_PATH[col][m]].temp_lock = False
					self.cell[COL_PATH[col][m]].removed_choices.remove(num)
					if num in self.cell[COL_PATH[col][m]].removed_choices:
						continue
					self.cell[COL_PATH[col][m]].choices.append(num)

				return -1
		return 0
	def __remove_n_s(self, sqr, num, n):
		for i in SQUARE_PATH[sqr]:
			if self.cell[i].locked == True:
				continue					

			if self.cell[i].temp_lock == False:
				self.cell[i].removed_choices.append(num)
				self.cell[i].temp_lock = True
			if num in self.cell[i].choices:
				self.cell[i].choices.remove(num)
			else:
				continue

			if len(self.cell[i].choices) == 0:
				for m in range(SQUARE_PATH[sqr].index(i)+1):
					print(i, SQUARE_PATH[sqr][m])
					if self.cell[SQUARE_PATH[sqr][m]].locked == True:
						continue					
					if len(self.cell[SQUARE_PATH[sqr][m]].removed_choices) == 0:
						continue
					self.cell[SQUARE_PATH[sqr][m]].temp_lock = False
					self.cell[SQUARE_PATH[sqr][m]].removed_choices.remove(num)
					if num in self.cell[SQUARE_PATH[sqr][m]].removed_choices:
						continue
					self.cell[SQUARE_PATH[sqr][m]].choices.append(num)

				return -1
		return 0

#remove only removes if num in choice.
#Add adds only if last num in removed choice,
#Adjacent cells can add 1 to removed choice only.
#Adjacent cells can remove multiple cells from removed choice.
	#Solution: Need flag to prevent multiple removals from removed choice.
	def __add_n_r(self, row, num):
		for i in ROW_PATH[row]:
			if self.cell[i].locked == True:
				continue
			if len(self.cell[i].removed_choices) == 0:
				continue
			if num in self.cell[i].removed_choices:
				self.cell[i].removed_choices.remove(num)
				if num in self.cell[i].removed_choices:
					continue
				self.cell[i].choices.append(num)

	def __add_n_c(self, col, num):
		for i in COL_PATH[col]:
			if self.cell[i].locked == True:
				continue
			if len(self.cell[i].removed_choices) == 0:
				continue
			if num in self.cell[i].removed_choices:
				self.cell[i].removed_choices.remove(num)
				if num in self.cell[i].removed_choices:
					continue
				self.cell[i].choices.append(num)

	def __add_n_s(self, sqr, num):
		for i in SQUARE_PATH[sqr]:
			if self.cell[i].locked == True:
				continue
			if len(self.cell[i].removed_choices) == 0:
				continue
			if num in self.cell[i].removed_choices:
				self.cell[i].removed_choices.remove(num)
				if num in self.cell[i].removed_choices:
					continue
				self.cell[i].choices.append(num)

	#TODO: if row successfully removes numbers in cells, if backtracking the choice list is not restored
	def __remove_n(self, n, num):
		if self.__remove_n_r(self.cell[n].r, num, n) == -1:
			return -1
		if self.__remove_n_c(self.cell[n].c, num, n) == -1:
			self.__add_n_r(self.cell[n].r, num)
			self.__unlock_r(self.cell[n].r)
			return -1
		if self.__remove_n_s(self.cell[n].s, num, n) == -1:
			self.__add_n_r(self.cell[n].r, num)
			self.__add_n_c(self.cell[n].c, num)
			self.__unlock_r(self.cell[n].r)
			self.__unlock_c(self.cell[n].c)
			return -1
		self.__unlock_r(self.cell[n].r)
		self.__unlock_c(self.cell[n].c)
		self.__unlock_s(self.cell[n].s)
		return 0

	def __solve(self, index):
		if index == (self.ranked_len-1):
			print('FINAL INDEX REACHED')
			return -1
		if self.ranked[index] == 44:
			print('we are are')
		self.cell[self.ranked[index]].locked = True
		for i in self.cell[self.ranked[index]].choices:
			print('choice', index,  self.cell[self.ranked[index]].choices)
			print('ptr', self.cell[self.ranked[index]].choice_ptr)
			print('compare', self.cell[self.ranked[index]].choices[self.cell[self.ranked[index]].choice_ptr])
			print('before', i, self.cell[self.ranked[index+1]].choices)
			if self.__remove_n(self.ranked[index+1], i) == -1:
				print('after', i, self.cell[self.ranked[index+1]].choices)
				self.cell[self.ranked[index]].choice_ptr += 1
				#self.__add_n_r(self.cell[self.ranked[index]].r, i)
				#self.__add_n_c(self.cell[self.ranked[index]].c, i)
				#self.__add_n_s(self.cell[self.ranked[index]].s, i)
				continue
			#print('choice', index, self.cell[self.ranked[10]].choices)
			#print('rchoice', index, self.cell[self.ranked[10]].removed_choices)
			if self.__solve(index+1) == -1:
				return -1
			self.cell[self.ranked[index]].choice_ptr += 1
			#print('before', i, self.cell[self.ranked[index+1]].choices)
			self.__add_n_r(self.cell[self.ranked[index]].r, i)
			self.__add_n_c(self.cell[self.ranked[index]].c, i)
			self.__add_n_s(self.cell[self.ranked[index]].s, i)
			#print('after', i, self.cell[self.ranked[index+1]].choices)
		self.cell[self.ranked[index]].choice_ptr = 0
		self.cell[self.ranked[index]].locked = False

	def __init__(self):
		self.myPuzzle = [j for i in p for j in i]#Unfold puzzle into 1d array

		self.cell = [Puzzle_Cell(n, self.myPuzzle[n]) for n in range(ELEMENTS)]
		for n in range(ELEMENTS):
			if self.cell[n].locked == True:
				continue

			self.__populate_col(n)
			self.__populate_row(n)
			self.__populate_square(n)
			self.ranked.append(n)
			#self.ranked_len.append(len(self.cell[n].choices))

		for i in range(len(self.ranked)):
			print(self.ranked[i])
		for i in range(len(self.ranked)):
			print(self.cell[self.ranked[i]].choices, self.cell[self.ranked[i]].removed_choices)
		self.ranked_len = len(self.ranked)


		#Sort list of cells in order of increasing choice sizes.
		#index = list(range(len(self.ranked)))
		#index.sort(key=self.ranked_len.__getitem__)
		#self.ranked[:] = [self.ranked[m] for m in index]
		#self.ranked_len = len(self.ranked)
		#for i in range(len(self.ranked)):
		#	print(self.cell[self.ranked[i]].choices)

		print('Begin Solving')
		self.__solve(0)
		print('RESULT')
		for i in range(ELEMENTS):
			print(self.cell[i].choice_ptr)
		for i in range(ELEMENTS):
			print(self.cell[i].choices, self.cell[i].removed_choices)
		for i in range(ELEMENTS):
			print(self.cell[i].temp_lock)
		solution = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		interim = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		for i in range(SECTORS):
			for n in range(SECTORS):
				interim[n] = (self.cell[i*9 + n].choices[self.cell[i*9 + n].choice_ptr])
			solution[i] = interim
			print(interim)


Puzzle = Puzzle()


#Finds the valid numbers the cell can be based on column
#def check_col(n):

#Finds the valid numbers the cell can be based on column
#def check_row(n):


#Finds the valid numbers the cell can be based on column
#def check_square(n):







#def build_puzzle(p):
#	for i in range(9):
#		row[i] = num for num in len
				