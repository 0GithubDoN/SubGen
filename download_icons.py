import os
import requests
from pathlib import Path

# Create icons directory if it doesn't exist
icons_dir = Path("icons")
icons_dir.mkdir(exist_ok=True)

# Dictionary of icon names and their URLs (using Material Design Icons)
icons = {
    # Original icons
    "browse.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/file/folder_open/materialicons/24dp/2x/baseline_folder_open_black_24dp.png",
    "down_arrow.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/navigation/arrow_drop_down/materialicons/24dp/2x/baseline_arrow_drop_down_black_24dp.png",
    "generate.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/av/play_circle/materialicons/24dp/2x/baseline_play_circle_black_24dp.png",
    "srt.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/description/materialicons/24dp/2x/baseline_description_black_24dp.png",
    "vtt.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/description/materialicons/24dp/2x/baseline_description_black_24dp.png",
    "embed.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/theaters/materialicons/24dp/2x/baseline_theaters_black_24dp.png",
    "language.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/translate/materialicons/24dp/2x/baseline_translate_black_24dp.png",
    "translate.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/translate/materialicons/24dp/2x/baseline_translate_black_24dp.png",
    "edit.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/image/edit/materialicons/24dp/2x/baseline_edit_black_24dp.png",
    "app_icon.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/av/subtitles/materialicons/24dp/2x/baseline_subtitles_black_24dp.png",
    
    # New icons for theme toggling
    "dark_mode.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/image/brightness_3/materialicons/24dp/2x/baseline_brightness_3_black_24dp.png",
    "light_mode.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/image/brightness_7/materialicons/24dp/2x/baseline_brightness_7_black_24dp.png",
    "theme.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/invert_colors/materialicons/24dp/2x/baseline_invert_colors_black_24dp.png",
    
    # Additional icons for improved UI
    "cancel.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/navigation/cancel/materialicons/24dp/2x/baseline_cancel_black_24dp.png",
    "save.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/content/save/materialicons/24dp/2x/baseline_save_black_24dp.png",
    "settings.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/settings/materialicons/24dp/2x/baseline_settings_black_24dp.png",
    "help.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/help/materialicons/24dp/2x/baseline_help_black_24dp.png"
}

# Download each icon
for icon_name, url in icons.items():
    response = requests.get(url)
    if response.status_code == 200:
        with open(icons_dir / icon_name, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {icon_name}")
    else:
        print(f"Failed to download {icon_name}")

print("\nAll icons downloaded successfully!")
print("Now run: pyrcc5 resources.qrc -o resources_rc.py")