@echo off
pushd %~dp0
..\code\tools\python27\python -u -B %~n0.py %*
popd
