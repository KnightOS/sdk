#include <display.h>

/* Warning! C support in KnightOS is highly expreimental. Your milage may vary. */

void main(void) {
	SCREEN *screen;
	get_lcd_lock();
	screen = create_screen();
	clear_buffer(screen);
	draw_str(screen, 0, 0, "Hello world!");
	fast_copy(screen);
	while (1);
}
