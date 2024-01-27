#!/bin/bash
while [ $# -gt 0 ];do
  key=${1}
  case ${key} in
    -i|--input)
      input=${2}
      shift 2
      ;;
    -o|--output)
      output=${2}
      shift 2
      ;;
    -x|--x)
      x=${2}
      shift 2
      ;;
    -y|--y)
      y=${2}
      shift 2
      ;;
    -z|--z)
      z=${2}
      shift 2
      ;;
    *)
      usage
      shift
      ;;  
  esac
done

echo The input is ${input},output is ${output},x is ${x},y is ${y},z is ${z} 1>>a.txt

single_tiff="single_tiff"
tif="3d_tif"

if [ ! -d "png" ];then
    mkdir png
else
    rm -rf png
    mkdir png
fi


if [ ! -d ${single_tiff} ];then
    mkdir ${single_tiff}
else
    rm -rf ${single_tiff}
    mkdir ${single_tiff}
fi


if [ ! -d ${tif} ];then
    mkdir ${tif} 
else
    rm -rf ${tif}
    mkdir ${tif}
fi

stltovoxel ${input} png/${output}.png --resolution-xyz ${x} ${y} ${z} 1>>a.txt

cd png
c=2
total_pngs=$(ls -l *.png | wc -l)

e1=$(printf "%02d" $((${total_pngs}-1)))
e2=$(printf "%02d" $((${total_pngs}-2)))
e3=$(printf "%02d" $((${total_pngs}-3)))

for f in *.png;
do
  if [ "$f" != *"_00.png" ] && [ "$f" != *"_01.png" ] && [ "$f" != *"_${e1}.png" ] && [ "$f" != *"_${e2}.png" ] && [ "$f" != *"_${e3}.png" ];then
  convert "$f" -gravity South -chop 0x${c} -gravity North -chop 0x${c} -gravity East -chop ${c}x0 -gravity West -chop ${c}x0 ../${single_tiff}/"${f%.*}.tiff";
  fi
done

# pwd
cd ../${single_tiff}
# pwd
convert *.tiff ../${tif}/${output}.tif