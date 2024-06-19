{ buildPythonPackage, setuptools, setuptools-scm, pypdf, horizon-eda }:

buildPythonPackage {
  pname = "horizon-utils";
  version = "0.1.0";
  src = ./.;
  format = "pyproject";
  nativeBuildInputs = [
    setuptools
    setuptools-scm
  ];
  propagatedBuildInputs = [
    pypdf
    horizon-eda
  ];
}
