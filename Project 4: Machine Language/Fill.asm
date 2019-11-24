// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(CHECK)
	@KBD
	D=M
	@FILL
	D;JNE
	@CLEAR
	0;JMP

(FILL)
	@color
	M=-1
	@SET
	0;JMP
	(CLEAR)
	@color
	M=0;
	@SET
	0;JMP

(SET)
	@8192
	D=A
	@i
	M=D
	@SCREEN
	D=A
	@cur
	M=D
	@LOOP
	0;JGT

(LOOP)
	@color
	D=M
	@cur
	A=M
	M=D
	@cur
	M=M+1
	@i
	MD=M-1
	@LOOP
	D;JGT
	@CHECK
	0;JMP
