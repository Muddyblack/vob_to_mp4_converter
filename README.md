# VOB_to_MP4_converter

This project helps converting your old DVD's into MP4 to preserve your treasures.

## Usage:

ATTENTION:
 - The preset is for computers with a nvidia graphic-card
 - Use ```-options``` and then ```-disable nvidia``` if there is no supported graphic-card
 - ```-help``` will show all options

To convert:
- Just copy and paste the full path of the folder with the VOB files
- If the VOB Files have standard-names it will seperate them in their different parts
- If not will it creates ```ONE``` big MP4 file of all VOB files in that folder
- If you want to convert just one file enter the full path of that file

Save some informations:
````python
#logsave
"""
 -hwaccel cuda -hwaccel_device 0 -hwaccel_output_format cuda
-c:v h264_nvenc -vf yadif_cuda=1 
.mp4
-c:a copy
"""

#ffmpeg standard code
#ffmpeg -i "concat:VTS_01_1.VOB|VTS_01_2.VOB|VTS_01_3.VOB" -c:v libx264 -vf yadif=1 new-video-h265.mp4 #software encoding
#ffmpeg -i "concat:VTS_01_1.VOB|VTS_01_2.VOB|VTS_01_3.VOB" -c:v h264_nvenc -vf yadif=1 new-video-h265B.mp4  #nvidia gpu encoding
```
