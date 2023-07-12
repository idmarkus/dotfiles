;(require 'cl)
;(require 'origami)
;
;;(define-key origami-mode-map "\C-\`" 'origami-forward-toggle-node)
;
;(global-set-key "\M-z" 'origami-forward-toggle-node)
(use-package dash)
(use-package s)

(use-package origami
  :init
  (require 'cl)
  :config
  (global-origami-mode 1)
  (global-set-key "\M--" 'origami-forward-toggle-node)
  (global-set-key (kbd "M-C--") 'origami-show-only-node))
  ;; (global-set-key "\C-j" 'origami-forward-fold)
  ;; (global-set-key "\C-k" 'origami-previous-fold))

(provide 'origami-config)
