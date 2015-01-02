@echo off
pushd %~dp0
..\tools\python27\python -u -B %~n0.py %*
popd
