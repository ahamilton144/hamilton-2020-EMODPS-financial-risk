CXX = mpiCC
CXXFLAGS = -c -Wall
INC = -I /opt/ohpc/pub/libs/gnu8/openmpi3/boost/1.70.0/include -I ./../../../misc
LIBS = -lm
UNAME_S = $(shell uname -s)

ifneq (, $(findstring SunOS, $(UNAME_S)))
	LIBS += -lnsl -lsocket -lresolv
endif
misc=./../../../misc

all: DPS_borgms DPS_retest

DPS_borgms: DPS_borgms.o moeaframework.o borgms.o mt19937ar.o
	$(CXX) DPS_borgms.o moeaframework.o borgms.o mt19937ar.o -o DPS_borgms

DPS_retest: DPS_retest.o moeaframework.o borgms.o mt19937ar.o
	$(CXX) DPS_retest.o moeaframework.o borgms.o mt19937ar.o -o DPS_retest

DPS_borgms.o: main.cpp $(misc)/borg/moeaframework.h $(misc)/boostutil.h $(misc)/borg/borgms.h
	$(CXX) $(CXXFLAGS) $(INC) main.cpp -o DPS_borgms.o

DPS_retest.o: main_retest.cpp $(misc)/borg/moeaframework.h $(misc)/boostutil.h $(misc)/borg/borgms.h
	$(CXX) $(CXXFLAGS) $(INC) main_retest.cpp -o DPS_retest.o

moeaframework.o: $(misc)/borg/moeaframework.c $(misc)/borg/moeaframework.h
	$(CXX) $(CXXFLAGS) $(misc)/borg/moeaframework.c

borgms.o: $(misc)/borg/borgms.c $(misc)/borg/borgms.h $(misc)/borg/borg.h
	$(CXX) $(CXXFLAGS) $(misc)/borg/borgms.c $(LIBS)

mt19937ar.o: $(misc)/borg/mt19937ar.c $(misc)/borg/mt19937ar.h
	$(CXX) $(CXXFLAGS) $(misc)/borg/mt19937ar.c $(LIBS)

clean:
	rm -rf *.o
	rm DPS_borgms
	rm DPS_retest

