#include "kernel.inc"
    .db "KEXC"
    .db KEXC_ENTRY_POINT
    .dw start
    .db KEXC_STACK_SIZE
    .dw 20
    .db KEXC_NAME
    .dw name
    .db KEXC_HEADER_END
name:
    .db "{{ project_name }}", 0
start:
    pcall(getLcdLock)
    pcall(getKeypadLock)

    pcall(allocScreenBuffer)
    pcall(clearBuffer)

    kld(hl, message)
    ld de, 0
    pcall(drawStr)

    pcall(fastCopy)

    pcall(flushKeys)
    pcall(waitKey)

    ret

message:
    .db "Hello, world!", 0
