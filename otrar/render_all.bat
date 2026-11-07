@echo off
cd /d "%~dp0"
"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" -b -P otrar_scenes.py -- --scene all --engine EEVEE --samples 64 --out renders
