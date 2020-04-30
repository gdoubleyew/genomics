CC=g++

programs = file_perf

all: $(programs)

file_perf: file_perf.cpp
	$(CC) -std=c++11 -o file_perf file_perf.cpp

clean:
	rm $(programs)
