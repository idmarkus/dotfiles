function! rust#bundles()
    NeoBundle 'rust-lang/rust.vim'
endfun

function! rust#enter()
    setf rust
    imap {<CR> {}<Esc>i<CR><Esc>kA<CR>
    imap {<S-CR> {}<Esc>i<CR><Esc>kA<CR>
    
    set foldmethod=syntax

endfun

function! rust#leave()
    set foldmethod=marker
endfun
