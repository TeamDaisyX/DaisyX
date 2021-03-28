
echo "
*********** STARTING DEPLOY ***********

DAISYX v2 -Base Aiogram
(C) 2020-2021 by @TEAMDAISYX
Support Chat is @DAISYSUPPORT_OFFICIAL.

***************************************
"
update_and_install_packages () {
    apt -qq update -y
    apt -qq install -y --no-install-recommends \
        git \
        ffmpeg \
        mediainfo \
        unzip \
        wget \
        gifsicle 
  }
  
install_helper_packages () {
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt -fqqy install ./google-chrome-stable_current_amd64.deb && rm google-chrome-stable_current_amd64.deb
    wget https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip && unzip chromedriver_linux64.zip && chmod +x chromedriver && mv -f chromedriver /usr/bin/ && rm chromedriver_linux64.zip
    wget -O opencv.zip https://github.com/opencv/opencv/archive/master.zip && unzip opencv.zip && mv -f opencv-master /usr/bin/ && rm opencv.zip
    wget https://people.eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel -P ./bot_utils_files/ai_helpers/
}

ech_final () {
    echo "
    
=++---------------------------------------------++=
DAISYX. Deployed Successfully

 ***************************
 * |D| |A| |I| |S| |Y| |X| *
 ******************* v2.0 ** 

Thanks for deploying DaisyX
(C) 2020-2021 by @TEAMDAISYX
Support Chat is @DAISYSUPPORT_OFFICIAL.
=++---------------------------------------------++=
                       Greetings from dev team :)
    "
}

_run_all () {
    UPDATE
    install_helper_packages
    pip3 install –upgrade pip
    pip3 install --no-cache-dir -r requirements.txt
    ech_final
}

_run_all
