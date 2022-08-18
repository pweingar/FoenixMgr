        .cpu "65816"

* = $004000

        .text 'PGX', $01
        .dword code1

;
; Code section
;
code1:  clc
        xce
        sep #$30
        .as
        .xs
        lda #'B'
        sta $afa000     ; Write A to the first cell of the text matrix
        lda #$f1
        sta $afc000     ; Write "white on black" to the first cell of color memory

dummy:  nop
        bra dummy
