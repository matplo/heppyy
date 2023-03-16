#!/bin/bash

echo "This is only doing symlinks to yasp.."

echo {{yasp.recipe_dir}}
#yasp --exec heppyy_dir=dirname {{yasp.recipe_dir}}

version=current

rm -rf {{prefix}}/lib/heppyy
mkdir -p {{prefix}}/lib
ln -sv {{heppyy_dir}}/heppyy {{prefix}}/lib

mkdir -p {{prefix}}/bin

recipe_file={{yasp.recipe_file}}
this_recipe_name={{yasp.recipe}}
current_dir={{yasp.current_dir}}

# {{heppyy_dir}}
