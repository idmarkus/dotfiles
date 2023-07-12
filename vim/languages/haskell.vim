function! haskell#bundles()
    NeoBundle 'godlygeek/tabular'
    NeoBundle 'Twinside/vim-haskellConceal'
"    NeoBundle 'enomsg/vim-haskellConcealPlus'
    NeoBundle 'travitch/hasksyn'
    NeoBundle 'Shougo/neocomplete.vim'
    NeoBundle 'eagletmt/neco-ghc'
    NeoBundle 'eagletmt/ghcmod-vim'
    NeoBundle 'raichoo/haskell-vim'
endfun

function! haskell#enter()
    setf haskell

    " Use two-space indentation
    setlocal shiftwidth=4
    setlocal tabstop=4
    setlocal softtabstop=4

    " Create tabularize mappings for aligning type signatures
"    AddTabularPattern! hs_type_sig / \?\(->\|::\|=>\)/l0r1
"    vnoremap <Leader>t :Tabularize //<Left>
"    inoremap -> -><ESC>:Tabularize hs_type_sig<CR>A
"    inoremap => =><ESC>:Tabularize hs_type_sig<CR>A

    " ...for aligning comments.
"    AddTabularPattern! hs_comment / \?--/l0r1
"    inoremap -- --<ESC>:Tabularize hs_comment<CR>A
 
    " Configuration for syntastic
    let g:syntastic_haskell_checkers=['ghc_mod']

    let ghc_args = ["fno-warn-unused-binds", "fno-warn-unused-imports", "fno-warn-name-shadowing", "fno-warn-orphans", "fobject-code", "fno-warn-type-defaults"]
    let g:ghcmod_hlint_options = ['--ignore=Redundant $']
    let sandbox = s:get_cabal_sandbox()
    if len(sandbox) != 0
        let package_db = split(globpath(sandbox, "*-packages.conf.d"), '\n')[0]
        call add(ghc_args, 'package-db=' . package_db)
    endif

    call map(ghc_args, '"-g -" . v:val')
    let ghc_args_string = join(ghc_args, ' ')

    let g:syntastic_haskell_ghc_mod_args=ghc_args_string
    let g:syntastic_haskell_hdevtools_args=ghc_args_string

    " TEMP: unsorted
    " Reload
""    map <silent> tu :call GHC_BrowseAll()<CR>
""    " Infer type
""    map <silent> tw :call GHC_ShowType(1)<CR>


endfun

function! haskell#leave()
    NeoCompleteDisable
endfun

function! s:get_cabal_sandbox()
    if filereadable('cabal.sandbox.config')
        let l:output = system('cat cabal.sandbox.config | grep local-repo')
        let l:dir = matchstr(substitute(l:output, '\n', ' ', 'g'), 'local-repo: \zs\S\+\ze\/packages')
        return l:dir
    else
        return ''
    endif
endfunction


function! PTest(arg1)
python << EOF
import vim
b = vim.current.buffer
argu1 = vim.eval("a:arg1")
b[0:0] = [argu1]
EOF
endfunction

function! Pragma(arg1)
python << EOF
import vim
b = vim.current.buffer
a1 = vim.eval("a:arg1")
strng = "{-# LANGUAGE " + a1 + " #-}"
b[0:0] = [strng]
EOF
endfunction
:command -nargs=1 Pragma call Pragma(<f-args>)
