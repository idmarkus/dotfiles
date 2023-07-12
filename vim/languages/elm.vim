function! elm#bundles()
    NeoBundle 'lambdatoast/elm.vim'
endfun

function! elm#enter()
    setf elm

    nnoremap <leader>el :ElmEvalLine<CR>
    vnoremap <leader>es :<C-u>ElmEvalSelection<CR>
    nnoremap <leader>em :ElmMakeCurrentFile<CR>
endfun
