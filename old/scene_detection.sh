ffmpeg -i 'output/cleaned_BIOENG320_lecture2(2023)_Prof-Yimon-AYE.mp4' -filter_complex "select='gt(scene,0.05)',metadata=print:file='output/lowering_threshold/detected_frames.txt'" -start_number 0 -fps_mode vfr output/lowering_threshold/img%03d.png
# conda env export | grep -v "^prefix: " > environment.yml
