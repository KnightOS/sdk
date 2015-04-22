#include <kernel.inc>
    .db "KEXC"
    .db KEXC_ENTRY_POINT
    .dw __start
    .db KEXC_STACK_SIZE
    .dw 20
    .db KEXC_NAME
    .dw __name
    .db KEXC_HEADER_END
__name:
    .db "example", 0
__start:
    call __relocate_data
    call __initialize_globals
    jp _main

_exit:
    ; Note: status code is discarded
    pcall(exitThread)
__exit_end:
.function _exit, _exit, _exit_end

__relocate_data:
    ; + 4 because the KEXC header has two static pointers
    ; TODO: There's probably a better way of doing that
    ld hl, __scas_relocatable_data + 4
.loop:
    ld e, (hl) \ inc hl
    ld d, (hl) \ inc hl
    ld bc, 0
    pcall(cpBCDE)
    ret z

    ex de, hl
    kld(bc, 0)
    add hl, bc
    push de
        ld e, (hl) \ inc hl
        ld d, (hl)
        ex de, hl \ add hl, bc \ ex de, hl
        ld (hl), d \ dec hl
        ld (hl), e
    pop de
    ex de, hl
    jr .loop

__initialize_globals:
    ; Note: this could be more optimized if we could toggle auto-relocation in code
    ld hl, __s_initialized_end
    ld bc, __s_initialized
    scf \ ccf
    sbc hl, bc
    ld b, h \ ld c, l
    ld a, b
    or c
    ret z
    ld hl, __s_initializer
    ld de, __s_initialized
    ldir
    ret

; Assign some labels to the start of some sections
.area _INITIALIZER
__s_initializer:
.area _INITIALIZED
__s_initialized:
.area _INITIALIZED_END
__s_initialized_end:
