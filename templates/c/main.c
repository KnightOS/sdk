#include <display.h>

/* Warning! C support in KnightOS is highly experimental. Your mileage may vary. */

void main(void) {
	SCREEN *screen;
	get_lcd_lock();
	screen = screen_allocate();
	screen_clear(screen);
	draw_string(screen, 0, 0, "Hello world!");
	screen_draw(screen);
	while (1);
}
