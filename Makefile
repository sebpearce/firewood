CFLAGS = -std=c99 -Wall -Werror

firewood: firewood.c
	cc $(CFLAGS) -o firewood firewood.c
