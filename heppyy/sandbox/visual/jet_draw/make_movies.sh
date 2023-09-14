for s in "img_graphs_akt" "img_graphs_ca" "img_graphs_cabg"
do
	ffmpeg -r 1 -i "${s}_%04d.png" -c:v libx264 -vf "fps=24,format=yuv420p" ${s}.mp4
done