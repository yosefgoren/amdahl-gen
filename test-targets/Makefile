TARGETS=fib-dynamic-gcc noploop cont

all: $(TARGETS)

cont: contention.c
	gcc $< -g -O0 -fopenmp -o $@

fib-dynamic-gcc: fib.c
	gcc $< -g -o $@

nops.o: nops.s
	gcc -O0 -g -c $< o $@

noploop: nops.s noploop.c
	gcc -O0 -g $^ -o $@

circle: circle.c
	gcc -l:libm.so $^ -o $@

clean:
	rm -f $(TARGETS)