	.text
	.file	"test.c"
	.global	add                     ! -- Begin function add
	.p2align	2
	.type	add,@function
add:                                    ! @add
! %bb.0:
	save %sp, -112, %sp
	mov	%i1, %i2 					
	mov	%i0, %i3
	st %i0, [%fp+-4]
	st %i1, [%fp+-8]
	ld [%fp+-4], %i0
	ld [%fp+-8], %i1
	add %i0, %i1, %i0
	st %i2, [%fp+-12]               ! 4-byte Folded Spill
	st %i3, [%fp+-16]               ! 4-byte Folded Spill
	ret
	restore
.Lfunc_end0:
	.size	add, .Lfunc_end0-add
                                        ! -- End function
	.globl	main                    ! -- Begin function main
	.p2align	2
	.type	main,@function
main:                                   ! @main
! %bb.0:
	save %sp, -96, %sp
	st %g0, [%fp+-4]
	mov	1, %o0
	call add
	mov	2, %o1
	ret
	restore %g0, %o0, %o0
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
                                        ! -- End function

	.ident	"clang version 8.0.0 "
	.addrsig
	.addrsig_sym add
