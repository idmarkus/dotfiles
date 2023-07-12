(use-package yafolding
  :config
  (define-key yafolding-mode-map (kbd "<C-S-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-M-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-return>") nil)
  (define-key yafolding-mode-map (kbd "M-C--") 'yafolding-toggle-all)
  (define-key yafolding-mode-map (kbd "M--") 'yafolding-toggle-element)
  (add-hook 'prog-mode-hook
            (lambda () (yafolding-mode))))

(provide 'yafolding-config)
