(require 's3r0-definitions
         (locate-file "s3r0-definitions.el" custom-theme-load-path
                      '("c" "")))

(create-s3r0-theme s3r0
                        s3r0-description (s3r0-color-definitions))
