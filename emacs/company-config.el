(global-company-mode)
(setq company-idle-delay 0)
(setq company-minimum-prefix-length 1)

;; Integrate with YASnippet and indentation
;(defun check-expansion ()
;  (save-excursion
;    (if (looking-at "\\_>") t
;      (backward-char 1)
;      (if (looking-at "\\.") t
;        (backward-char 1)
;        (if (looking-at "->") t nil)))))
;
;(defun do-yas-expand ()
;  (let ((yas/fallback-behavior 'return-nil))
;    (yas/expand)))
;
;(defun tab-indent-or-complete ()
;  (interactive)
;  (if (minibufferp)
;      (minibuffer-complete)
;    (if (or (not yas/minor-mode)
;            (null (do-yas-expand)))
;        (if (check-expansion)
;            (company-complete-selection)
;          (indent-for-tab-command)))))
;; -- Integrate with YASnippet and indentation


;(defun insert-spc ()
;  (interactive)
;  (insert-char 32))

;(define-key company-active-map (kbd "<tab>") 'company-complete-common-or-cycle)
;(define-key company-active-map (kbd "<return>") 'company-complete-selection)
;(define-key company-active-map (kbd "M-j") 'newline)
;(define-key company-active-map (kbd "M-l") 'insert-spc)
