(use-package vimish-fold
  :config
  (global-set-key "\M--" 'vimish-fold-toggle)
  (global-set-key (kbd "M-C--") 'vimish-fold-toggle-all)
  (vimish-fold-global-mode 1))

(provide 'vimish-fold-config)
