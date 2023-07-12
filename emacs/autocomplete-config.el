(use-package auto-complete
  :config
  (require 'auto-complete-config)
  (ac-config-default))

;;(require 'auto-complete)
;(require 'auto-complete-config)
;(ac-config-default)

;(defun ac-config-init ()
;  (require 'auto-complete-config)
;  (ac-config-default))
;
;(use-package auto-complete
;  :config (ac-config-init))
;
;(defun ac-c-header-init ()
;  (use-package auto-complete-c-headers
;    :config (add-to-list 'ac-sources 'ac-source-c-headers)))

;; auto-complete-c-headers
;; TODO: move this to c-mode config?
(defun ac-c-header-init ()
  (use-package 'auto-complete-c-headers)
  (add-to-list 'ac-sources 'ac-source-c-headers))

(add-hook 'c-mode-hook 'ac-c-header-init)
(add-hook 'c++-mode-hook 'ac-c-header-init)

(provide 'autocomplete-config)
