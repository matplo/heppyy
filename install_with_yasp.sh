#!/usr/bin/env bash

function thisdir()
{
        SOURCE="${BASH_SOURCE[0]}"
        while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
          DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
          SOURCE="$(readlink "$SOURCE")"
          [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
        done
        DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
        echo ${DIR}
}
THISD=$(thisdir)

echo ${THISD}

yasp_exec=$(which yasp)

if [ -z "${yasp_exec}" ]; then
    echo "[e] please use yasp at https://github.com/matplo/yasp"
else
    echo "[i] using yasp at ${yasp_exec}"
    ${yasp_exec} --recipe-dir ${THISD}/yasp_recipe -r heppyy -m
fi
