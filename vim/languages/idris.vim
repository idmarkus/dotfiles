function! idris#bundles()
    NeoBundle 'idris-hackers/idris-vim'
endfun

function! idris#enter()
    setf idris
    let g:maplocalleader=' '

    " Indentations:
    let g:idris_indent_if = 3
    let g:idris_indent_case = 5
    let g:idris_indent_let = 4
    let g:idris_indent_where = 6
    let g:idris_indent_do = 3
    let g:idris_indent_rewrite = 8

    " Enable concealing:
    let g:idris_conceal = 1

    " Sanity check:
    syntax on

endfun
