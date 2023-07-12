(use-package js2-mode
  :config
  (add-to-list 'auto-mode-alist '("\\.js\\'" . js2-mode))
  (add-to-list 'auto-mode-alist '("\\.hjs\\'" . js2-mode)))

;; Keys
(setq taken-keys (list "\M-j" "\M-k"))
(dolist (key taken-keys) (define-key js2-mode-map key nil))


;; Stuff

(setq-default js2-allow-rhino-new-expr-initializer nil)
;; (setq-default js2-auto-indent-p nil)
;; (setq-default js2-enter-indents-newline nil)
(setq-default js2-global-externs '("module" "require" "buster" "sinon" "assert" "refute" "setTimeout" "clearTimeout" "setInterval" "clearInterval" "location" "__dirname" "console" "JSON"))
(setq-default js2-idle-timer-delay 0.1)
;; (setq-default js2-indent-on-enter-key nil)
(setq-default js2-mirror-mode nil)
(setq-default js2-strict-inconsistent-return-warning nil)
(setq-default js2-auto-indent-p t)
(setq-default js2-include-rhino-externs nil)
(setq-default js2-include-gears-externs nil)
(setq-default js2-concat-multiline-strings 'eol)
(setq-default js2-rebind-eol-bol-keys nil)

;; Let flycheck handle parse errors
(setq-default js2-show-parse-errors nil)
;; (setq-default js2-strict-missing-semi-warning nil)
;; (setq-default js2-strict-trailing-comma-warning t) ;; jshint does not warn about this now for some reason

(add-hook 'js2-mode-hook (lambda () (flycheck-mode 1)))


;; Aesthetics
(font-lock-add-keywords
 'js2-mode `(("\\(function\\) *("
              (0 (progn (compose-region (match-beginning 1)
                                        (match-end 1) "\u0192")
                        nil)))))

;; Use right arrow for return in one-line functions
(font-lock-add-keywords
 'js2-mode `(("function *([^)]*) *{ *\\(return\\) "
              (0 (progn (compose-region (match-beginning 1)
                                        (match-end 1) "\u2190")
                        nil)))))


;; Funct;; ions
;; (defun my-js-electric-brace ()
;;   (interactive)
;;   (insert "{")
;;   (let ((pps (syntax-ppss)))
;;     (when (and (eolp) (not (or (nth 3 pps) (nth 4 pps)))) ;; EOL and not in string or comment
;;       (c-indent-line)
;;       (insert "\n\n}")
;;       (c-indent-line)
;;       (forward-line -1)
;;       (c-indent-line))))

;; (defun delete-block ()
;;   (search-backward "{")
;;   (zap-to-char 1 ?}))

;; (defun delete-block-or-hungry-backward-char ()
;;   (interactive)
;;   (if (and (looking-at "[\n[:space:]]*}")
;;            (looking-back "{[\n[:space:]]*"))
;;       (delete-block)           ; then
;;     (hungry-backward-delete-char))) ; else

;; (defun insert-block-or-normal-brace ()
;;   (interactive)
;;   (if (looking-back "\n[? ?\t]*")
;;       (my-electric-brace)
;;     (c-electric-brace 1))) 


(defun js-hook-setup ()
  ;; (define-key js-mode-map "{" 'insert-block-or-normal-brace)
  (define-key js-mode-map [backspace] 'delete-block-or-hungry-backward-char)
  (define-key js-mode-map [C-backspace] 'hungry-backward-kill-word))

(add-hook 'js2-mode-hook 'js-hook-setup) ;; Make this more eloquent?

(provide 'setup-javascript)
