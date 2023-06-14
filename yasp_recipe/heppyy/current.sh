#!/bin/bash

function abspath()
{
  case "${1}" in
    [./]*)
    echo "$(cd ${1%/*}; pwd)/${1##*/}"
    ;;
    *)
    echo "${PWD}/${1}"
    ;;
  esac
}
export -f abspath

# echo "This is only doing symlinks to yasp.."

echo "[i] Recipe dir is: {{yasp.recipe_dir}}"
#yasp --exec heppyy_dir=dirname {{yasp.recipe_dir}}

version=current

rm -rf {{prefix}}/lib/heppyy
mkdir -p {{prefix}}/lib
ln -sv {{heppyy_dir}}/heppyy {{prefix}}/lib

mkdir -p {{prefix}}/bin

recipe_file={{yasp.recipe_file}}
this_recipe_name={{yasp.recipe}}
current_dir={{yasp.current_dir}}

srcdir=$(abspath {{yasp.recipe_dir}}/../heppyy)
cd {{builddir}}
echo "[i] source dir is {{srcdir}}"
cmake -DCMAKE_INSTALL_PREFIX={{prefix}} \
	-DCMAKE_BUILD_TYPE=Release \
	{{srcdir}} && cmake --build . --target install -- -j {{n_cores}}
# {{heppyy_dir}}
