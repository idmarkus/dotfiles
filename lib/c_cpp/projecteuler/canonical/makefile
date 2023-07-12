CXX = g++

# Use D="CUSTOM_DEFINITION" for injecting -D flags on the command line.
# i.e. make D="DEF1 DEF2" etc.
D =

DEFS =
DEFS += $(D)
DEFFLAGS := $(patsubst %, -D"%", $(DEFS))
#DEFFLAGS := $(patsubst %, -D\"%\", $(DEFS))

CXXFLAGS = -march=native -O3 -Wall -c $(DEFFLAGS) -std=c++14 -I../../headers
CXXFLAGS_MEEK = -Wall -c -std=c++14 -I../headers
LDFLAGS =

EXE = binary.out
MEEK = meek.out

all: $(EXE)

$(EXE): main.o
	$(CXX) $< $(LDFLAGS) -o $@

main.o: main.cpp
	$(CXX) $(CXXFLAGS) $< -o $@


meek: $(MEEK)

$(MEEK): meek.o
	$(CXX) $< $(LDFLAGS) -o $@

meek.o: main.cpp
	$(CXX) $(CXXFLAGS_MEEK) $< -o $@

clean:
ifneq ("$(wildcard *.o)", "")
	rm *.o
endif
