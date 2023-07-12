(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(origami-show-fold-header nil)
 '(show-paren-mode t)
 '(tool-bar-mode nil))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 ;; '(default ((t (:family "DejaVu Sans Mono" :foundry "PfEd" :slant normal :weight normal :height 113 :width normal))))
 '(default ((t (:family "Cousine" :slant normal :weight normal :height 113 :width normal :antialias natural))))
 '(origami-fold-header-face ((t (:background "#073642" :box (:line-width 1 :color "#073642"))))))

;; Setup load-path
;; (defvar config-dir (concat (getenv "HOME") "/code/dotfiles/emacs"))
;; (setq load-path (cons (concat (getenv "HOME") "/code/dotfiles/emacs") load-path))
(defvar config-dir (concat (getenv "HOME") "/code/dotfiles/emacs"))
(setq load-path (cons config-dir load-path))

;; Backups
;; (defvar backup-dir (concat config-dir "/.backup"))
(setq backup-directory-alist '(("." . "~/code/dotfiles/emacs/.backup"))
      ;auto-save-file-name-transforms '((".*" temporary-file-directory t))
      backup-by-copying t
      delete-old-versions t
      kept-new-versions 6
      kept-old-versions 2
      version-control t)

;; Enable package, add melpa and elpa to package list
(require 'package)
(add-to-list 'package-archives
	     '("melpa" . "https://melpa.org/packages/")
	     '("elpa" . "http://elpa.gnu.org/packages/"))
(package-initialize)

;; Enable use-package
(require 'use-package)
(setq use-package-always-ensure t)
(require 'bind-key) ;use-package's bind-key
(require 'diminish) ;use-package's diminish

(require 'general)
(require 'keys)
(require 'color)
(require 'funcs)
(require 'window-management)

;; Packages' configs
(require 'yasnippet-config)
(require 'autocomplete-config)
(require 'autopair-config)
(require 'flycheck-config)
(require 'ido-config)
(require 'cl-config)
(require 'origami-config)
(require 'eshell-config)
(require 'grunt-config)

;; (require 'vimish-fold-config)
;; (require 'neotree-config)
;; (require 'sublimity-config)
;; (load-library "company-config")
;; (load-library "iedit-config")
;; (require 'paredit-config)

;; Languages configs
(load-library "lang/c-common")
(load-library "lang/elisp")
(load-library "lang/rust")
(load-library "lang/setup-javascript")
(load-library "lang/setup-lua")
