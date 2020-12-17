# Johnny Li
# Assignment 1
# Makefile C

# --- macros
CC=cc

# --- targets
# --- makefile
c_program: c_program.o
	$(CC) -o c_program c_program.o

c_program.o: c_program.c
	$(CC) -c c_program.c
