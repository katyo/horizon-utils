{ pkgs ? import <nixpkgs> {} }:
with pkgs;
let python = python3.withPackages (py: with py; [
      horizon-eda
      pypdf
    ]);
in mkShell {
  buildInputs = [ python ];
}
