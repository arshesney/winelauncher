#!/bin/bash
# $1 prefix
# $2 arch
# $3 version
# $4+ exe
if [ $# -eq 0 ]; then
    echo "Usage: $0 <bottle> <arch> <version> <executable>"
    exit 1
fi

BASE_PREFIX="$HOME/.local/wineprefixes"
WINEPREFIX="${BASE_PREFIX}/${1}"
LOGFILE="${WINEPREFIX}/wine.out"
LOGGER_TAG="${1}"

WINEARCH="${2}"
if [[ $WINEARCH == 32 || $WINEARCH == 64 ]]; then
    WINEARCH="win$WINEARCH"
fi

if [ -d "/opt/wine/wine-${3}" ]; then
    wine_path="/opt/wine/wine-${3}"
else
    wine_path=/usr
fi

PATH=$wine_path/bin:$PATH
LD_LIBRARY_PATH="$wine_path/lib:$LD_LIBRARY_PATH"
WINEDLLPATH=$wine_path/lib/wine
if [[ $WINEARCH == "win64" ]]; then
    LD_LIBRARY_PATH="$wine_path/lib32:$LD_LIBRARY_PATH"
else
    WINEDLLPATH=$wine_path/lib32/wine
fi
WINEVERPATH=$wine_path
WINESERVER=$wine_path/bin/wineserver
WINELOADER=$wine_path/bin/wine

#if [ -z ${WINEDEBUG} ]; then
#    WINEDEBUG="-all"
#fi
#if [ -z ${NINEDEBUG} ]; then
#    NINEDEBUG="-all"
#fi

#export PATH LD_LIBRARY_PATH WINEVERPATH WINEPREFIX WINEARCH WINESERVER WINELOADER WINEDLLPATH WINEDEBUG NINEDEBUG
WINE_ENV="PATH=${PATH} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} WINEVERPATH=${WINEVERPATH} WINEPREFIX=${WINEPREFIX} WINEARCH=${WINEARCH} WINESERVER=${WINESERVER} WINELOADER=${WINELOADER} WINEDLLPATH=${WINEDLLPATH} WINEDEBUG=${WINEDEBUG} NINEDEBUG=${NINEDEBUG}"

if [ -z ${LD_PRELOAD} ]; then
    WINE_ENV="LD_PRELOAD=${LD_PRELOAD} ${WINE_ENV}"
fi

shift 3
if [ "${1}" == "winetricks" ]; then
    shift
    /bin/bash -c "$WINE_ENV winetricks $* 2>&1 | logger -t ${LOGGER_TAG}"
elif
    [ "${1}" == "export-steam" ]; then
    shift
    /bin/sh -c "$WINE_ENV regedit -E ~/Documenti/steam.reg HKEY_LOCAL_MACHINE\\\\Software\\\\Valve"
elif
    [ "${1}" == "import-steam" ]; then
    shift
    /bin/sh -c "$WINE_ENV regedit ~/Documenti/steam.reg"
else
    sudo ip netns exec wine sudo -u ${USER} $WINE_ENV $WINELOADER "${@}" 2>&1 | logger -t ${LOGGER_TAG}
fi

exit 0
