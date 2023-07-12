(require 'solarized-gray-definitions
         (locate-file "solarized-gray-definitions.el" custom-theme-load-path
                      '("c" "")))

(create-solarized-gray-theme solarized-gray
                        solarized-gray-description (solarized-gray-color-definitions))
