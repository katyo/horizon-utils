{ pkgs ? import <nixpkgs> {}, ... }:
{
  nixpkgs.overlays = [ (import ./overlay.nix) ];
}
