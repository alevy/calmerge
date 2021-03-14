{ pkgs ? import <nixpkgs> {}}:

with pkgs;

python3Packages.buildPythonPackage {
  name = "calmerge";
  src = ./.;
  propagatedBuildInputs = [ python3Packages.icalendar python3Packages.pyyaml ];
}
