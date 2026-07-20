#!/bin/bash

cd /home/steffen/Experiments/2024/iot/cal_kit1/

# rsync -a -q -e ssh iot@192.168.4.97:iot-systems/data/water_level/ ./water_level
# rsync -a -q -e ssh iot@192.168.4.97:iot-systems/data/CO2/ ./CO2
rsync -a -q -e ssh smear@smeartartu.emu.ee:DataLog/IOT/CO2-SCT1-2M/ ./CO2
rsync -a -q -e ssh smear@smeartartu.emu.ee:DataLog/IOT/WATER-SCT1-GR/ ./water_level/
rsync -a -q -e ssh smear@smeartartu.emu.ee:DataLog/GR/GR_WeatherInformation_NEW ./meteo

cd /home/steffen/Experiments/2024/iot/cal_kit1/meteo

./makeMeteoCsv.sh 

cd /home/steffen/Experiments/2024/iot/cal_kit1/

