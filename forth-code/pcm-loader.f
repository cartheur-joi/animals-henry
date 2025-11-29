\ ==============================================================
\  PCM16 Mono Loader (for ref.raw and test.raw)
\  --------------------------------------------------------------
\  Loads a raw 16-bit little-endian mono PCM file into memory.
\  Leaves on stack:  ( sample-addr n-samples )
\  Also prints: "Loaded <n> samples from: <filename>"
\ 
\  Requires:
\    open-file  file-size  read-file  close-file
\    allocate   free
\    c@  !  type  throw  etc.
\  Tested with Gforth (uses file-size, not file-size@).
\ ==============================================================

decimal

\ --------------------------------------------------------------
\ Utility: error handling
\ --------------------------------------------------------------

: ?ior ( ior -- )
  \ If ior is non-zero, THROW it.
  ?dup IF throw THEN ;

\ --------------------------------------------------------------
\ Globals
\ --------------------------------------------------------------

variable source-fname-addr   \ c-addr of last loaded filename
variable source-fname-len    \ length of last loaded filename

variable pcm-bytes           \ even byte size of file
variable pcm-byte-buf        \ address of temporary byte buffer

variable samples-count       \ number of 16-bit samples
variable samples-buf         \ address of final sample cell buffer

\ --------------------------------------------------------------
\ Convert 2 little-endian bytes to signed 16-bit in cell
\   ( c-addr -- n )
\ --------------------------------------------------------------
: le-16@ ( c-addr -- n )
  \ Read: low byte then high byte, combine, sign-extend.
  dup 1+ c@ 256 *           \ high byte * 256
  swap c@ +                 \ + low byte => u16 [0..65535]
  dup 32768 >= IF           \ if sign bit set
    65536 -                 \ convert to negative in [-32768..-1]
  THEN ;

\ --------------------------------------------------------------
\ Convert byte buffer (16-bit LE samples) into cell buffer
\   ( byte-addr sample-addr n-samples -- )
\ --------------------------------------------------------------
: bytes>cells ( byte-addr sample-addr n-samples -- )
  0 ?DO
    over I 2 * +            \ byte-addr + 2*i
    le-16@                  \ -> sample
    over I cells +          \ sample-addr + i*cells
    !                       \ store
  LOOP
  2drop ;                   \ drop byte-addr and sample-addr

\ --------------------------------------------------------------
\ Core loader
\   ( c-addr u -- sample-addr n-samples )
\ --------------------------------------------------------------
: load-pcm ( c-addr u -- sample-addr n-samples )
  \ Save filename for later printing
  2dup
  source-fname-addr !
  source-fname-len !

  \ Open file read-only
  r/o open-file ?ior        \ -- fileid
  >r                        \ save fileid on return stack

  \ Determine file size (assumes size fits in one cell)
  r@ file-size ?ior         \ -- ud
  drop                      \ keep low cell only: -- u-bytes

  \ Force even size (clear low bit: ignore trailing odd byte)
  1 invert and              \ u-even
  dup pcm-bytes !           \ remember even byte count

  \ Allocate temporary byte buffer
  pcm-bytes @ allocate ?ior \ -- addr
  dup pcm-byte-buf !        \ store temporary buffer address

  \ Read entire file into byte buffer
  pcm-byte-buf @            \ c-addr
  pcm-bytes @               \ u
  r@                        \ fileid
  read-file ?ior            \ -- actual-u
  drop                      \ ignore actual count (assume full read)

  \ Close file
  r> close-file ?ior        \ return stack now balanced

  \ Compute number of 16-bit samples: bytes / 2
  pcm-bytes @ 2 / dup samples-count !   \ -- n-samples

  \ Allocate final cell buffer for samples
  dup cells allocate ?ior              \ n-samples -- n-samples addr
  dup samples-buf !                    \ store buffer address
  drop                                  \ keep n-samples in variable only

  \ Convert from byte buffer into cell buffer
  pcm-byte-buf @
  samples-buf @
  samples-count @
  bytes>cells

  \ Free temporary byte buffer
  pcm-byte-buf @ free ?ior

  \ Leave ( sample-addr n-samples ) on data stack
  samples-buf @ samples-count @

  \ Print verification line (does not disturb result)
  cr
  ." Loaded " samples-count @ . ." samples from: "
  source-fname-addr @ source-fname-len @ type
  cr
;

\ --------------------------------------------------------------
\ Convenience wrappers for two input files
\ --------------------------------------------------------------
\ ref.raw  : contains the phrase to be identified
\ test.raw : contains the phrase mixed with other content
\ --------------------------------------------------------------

: load-ref  ( -- ref-addr ref-n )
  s" ref.raw" load-pcm ;

: load-test ( -- test-addr test-n )
  s" test.raw" load-pcm ;

\ Example interactive usage in Gforth:
\   load-ref   \ -> ref-addr ref-n
\   load-test  \ -> ref-addr ref-n test-addr test-n
\ You can then perform your matching / search using those buffers.
\ 
\ NOTE: The caller owns the returned sample buffers.
\ To free a loaded buffer later, do:
\   <sample-addr> free ?ior
\ (Keep track of each address from load-ref / load-test.)
\ --------------------------------------------------------------
