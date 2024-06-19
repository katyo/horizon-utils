self: super: {
  horizon-utils = self.python3.pkgs.callPackage ./package.nix {};
}
