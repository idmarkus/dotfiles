(define-key emacs-lisp-mode-map "\M-p" 'eval-buffer)

(add-hook 'emacs-lisp-mode-hook
          (lambda ()
            (setq autopair-dont-activate t)))
