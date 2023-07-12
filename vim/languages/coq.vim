function! coq#bundles()
    NeoBundle 'the-lambda-church/coquille'
    NeoBundle 'def-lkb/vimbufsync'
endfun

function! coq#enter()
    setf coq

    call coquille#FNMapping()
    CoqLaunch

    hi CheckedByCoq guibg=#073642
    hi SentToCoq guibg=#073642
endfun
