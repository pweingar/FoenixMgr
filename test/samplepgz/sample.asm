        .cpu "65816"

* = $004000

        .byte 'Z'

;
; Code section
;
        .long code1
        .long code2-code1
code1:  clc
        xce
        sep #$30
        .as
        .xs
        lda #'a'
        sta $afa000     ; Write A to the first cell of the text matrix
        lda #$f1
        sta $afc000     ; Write "white on black" to the first cell of color memory

dummy:  nop
        bra dummy

code2:

;
; Start Address section
;
        .long   code1   ; Start address
        .long   0       ; 0 data is in this section
