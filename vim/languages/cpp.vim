function! cpp#bundles()
    "NeoBundle 'octol/vim-cpp-enhanced-highlight'
    
    NeoBundleLazy 'jeaye/color_coded', {
          \ 'build': {
          \   'unix': 'cmake . && make && make install',
          \ },
          \ 'autoload' : { 'filetypes' : ['c', 'cpp', 'objc', 'objcpp'] },
          \ 'build_commands' : ['cmake', 'make']
      \}
"    NeoBundle 'LucHermitte/lh-vim-lib'
"    NeoBundle 'LucHermitte/lh-tags'
"    NeoBundle 'LucHermitte/lh-dev'
"    NeoBundle 'LucHermitte/lh-brackets'
"    NeoBundle 'LucHermitte/searchInRuntime'
"    NeoBundle 'LucHermitte/mu-template'
"    NeoBundle 'tomtom/stakeholders_vim'
"    NeoBundle 'LucHermitte/lh-cpp'
endfun

function! cpp#enter()
    "setf cpp
    "SyntasticToggleMode
    
    imap {<CR> {}<Esc>i<CR><Esc>kA<CR>
    imap {<S-CR> {}<Esc>i<CR><Esc>kA<CR>
    
    set foldmethod=syntax

    let g:ycm_always_populate_location_list = 0

    "let g:syntastic_cpp_compiler = "clang++"
    "let g:syntastic_cpp_compiler_options = "-std=c++11"
endfun

function! cpp#leave()
    set foldmethod=marker
    "SyntasticToggleMode
endfun
