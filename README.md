# Horizon-EDA utilities

## Utilities

### brd2tpl

This tool intended to export board as proto template.

```
usage: brd2tpl [-h] [-f FIELD] [-m MARGIN] [-b BORDER] [-d HOLE] [-r ROTATE] [-c MARKER_PDF] [-p MARKER_OFFSET] input output

Export horizon-eda board to photo template

positional arguments:
  input                 Project to export
  output                PDF file to export to

options:
  -h, --help            show this help message and exit
  -f FIELD, --field FIELD
                        The top field width (mm)
  -m MARGIN, --margin MARGIN
                        The margin distance (mm)
  -b BORDER, --border BORDER
                        The border width (mm)
  -d HOLE, --hole HOLE  The hole diameter (mm)
  -r ROTATE, --rotate ROTATE
                        The rotation angle (deg)
  -c MARKER_PDF, --marker-pdf MARKER_PDF
                        The PDF file to use as marker
  -p MARKER_OFFSET, --marker-offset MARKER_OFFSET
                        The marker to corner distance (mm)

See https://github.com/katyo/horizon-utils
```

Export board from project with rotation and markers at corders:
```
brd2tpl -c marker.pdf -r 90 project.hprj board-tpl.pdf
```

## Installation

### NixOS

Add channel:
```
$ sudo nix-channel --add https://github.com/katyo/horizon-utils/archive/master.tar.gz horizon-utils
$ sudo nix-channel --update horizon-utils
```

Edit config:
```
imports = [ <horizon-utils> ];
environment.systemPackages = with pkgs; [ horizon-utils ];
```
