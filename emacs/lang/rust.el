
(add-to-list 'auto-mode-alist '("\\.rs\\'" . rust-mode))


;; Racer
(setq racer-cmd "/usr/bin/racer")
(setq racer-rust-src-path (substitute-in-file-name "$HOME/.rust/src"))

  ;; Company
(setq company-tooltip-align-annotations t)

(add-hook 'rust-mode-hook
          '(lambda ()
             (rustfmt-enable-on-save)
             (racer-activate)
             (racer-turn-on-eldoc)
             (add-hook 'flyckeck-mode-hook #'flycheck-rust-setup)
             (set (make-local-variable 'company-backends) '(company-racer))
             (local-set-key (kbd "M-.") #'racer-find-definition)
             (local-set-key (kbd "TAB") #'racer-complete-or-indent)
             ))
