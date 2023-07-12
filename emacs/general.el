;(global-linum-mode 1)
;(which-function-mode 1)
;(electric-pair-mode 1)
(setq-default indent-tabs-mode nil)
(global-prettify-symbols-mode 1)

;; GUI
(menu-bar-mode 0)                       ; No menubar
(scroll-bar-mode 0)                     ; No scrollbar
(tool-bar-mode 0)                       ; No toolbar
(blink-cursor-mode 0)                   ; No blinking
(setq pop-up-windows nil)               ; No popup windows

(setq inhibit-startup-echo-area-message t) ; No startup screen
(setq inhibit-startup-message t)           ; -||-

(use-package linum
  :config
  (setq linum-format " %3d ")
  (dolist (hook (list 'emacs-lisp-mode-hook
                      'python-mode-hook
                      'tex-mode-hook
                      'latex-mode-hook
                      'c-mode-hook
                      'text-mode-hook
                      'rst-mode-hook
                      'c++-mode-hook))
    (add-hook hook 'linum-mode))
  (global-linum-mode 1))
(use-package hlinum)

;; ----------------------------------------------------------------------------
;; Headerline
;; ----------------------------------------------------------------------------
(defun mode-line-fill (face reserve)
  "Return empty space using FACE and leaving RESERVE space on the right."
  (unless reserve
    (setq reserve 20))
  (when (and window-system (eq 'right (get-scroll-bar-mode)))
    (setq reserve (- reserve 3)))
  (propertize " "
              'display `((space :align-to (- (+ right right-fringe right-margin) ,reserve)))
              'face face))

(setq-default header-line-format (list
   " "
   'mode-line-mule-info
   'mode-line-modified
   "  "
   'mode-line-buffer-identification
   'mode-line-modes
   " -- "
   `(vc-mode vc-mode)

   ;; File read-only
   '(:eval (if buffer-read-only
               (list (mode-line-fill 'nil 13)
                     (propertize " [read-only] " 'face 'header-line-grey))))

   ;; File modified
   '(:eval (if (buffer-modified-p)
               (list (mode-line-fill 'nil 12)
                     (propertize " [modified] " 'face 'header-line-red))
             (list (mode-line-fill 'nil 9)
                   (propertize "%4l:%3c " 'face 'header-line))))
   ))
(setq-default mode-line-format (list ""))
;; (set-face-attribute 'mode-line nil
;;                     :height 10
;;                     :background "#999"
                    ;; :box nil)

;; ----------------------------------------------------------------------------
;; Geometry
;; ----------------------------------------------------------------------------
;; Fringe on left and right: 8 pixels
(fringe-mode '(8 . 8))

;; ;; Internal border: 32 pixels
;; (modify-frame-parameters (selected-frame)
;;                          '((internal-border-width . 8)))
;; ;; Default frame size and border
;; (setq default-frame-alist (append (list
;;                            '(width . 88) '(height .  42)
;;                            '(top   . 50) '(left   . 250)
;;                            '(internal-border-width . 8))
;;                            default-frame-alist))

(setq-default frame-title-format "%b")
(setq         frame-title-format "%b")


;; Aesthetics
(show-paren-mode 1)

;; Interaction
(fset 'yes-or-no-p 'y-or-n-p) ;; (yes/no) -> (y/n)
(setq scroll-step 1)

(add-hook 'emacs-startup-hook 'eshell)

(require 'uniquify)
(setq uniquify-buffer-name-style 'reverse)
(setq uniquify-separator "||")
(setq uniquify-after-kill-buffer-p t) ; rename after killing uniquified
(setq uniquify-ignore-buffers-re "^\\*") ; don't bother special buffers

(provide 'general)
