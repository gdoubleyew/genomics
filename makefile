CC=g++

programs = file_perf

all: $(programs)

# note: c++11 or c++14 work
file_perf: file_perf.cpp
	$(CC) -std=c++11 file_perf.cpp -lstdc++fs -o file_perf

clean:
	rm $(programs)
