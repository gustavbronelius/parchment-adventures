# File: themes.py

class Theme:
    def __init__(self, name, background_image, text_color, console_bg_color):
        self.name = name
        self.background_image = background_image
        self.text_color = text_color
        self.console_bg_color = console_bg_color

# Themes are now defined as a list
themes_list = [
    Theme("light", "../assets/images/scroll.png", "#000000", "#FFFFFF"),  # Black text on white background
    Theme("dark", "../assets/images/scroll.png", "#FFFFFF", "#000000"),  # White text on black background
    Theme("horror", "../assets/images/horror.png", "#FF0000", "#0D0D0D"),  # Red text on dark gray background
    Theme("sci-fi", "../assets/images/scifi.png", "#7FFFD4", "#001a33"),  # Aquamarine text on deep navy blue background
    Theme("cyberpunk", "../assets/images/cyberpunk.png", "#FF00FF", "#2a004d"),  # Magenta text on dark purple background
    Theme("adventure", "../assets/images/adventure.png",  "#DAA520", "#800000"),  # Yellow text on red background
    Theme("steampunk", "../assets/images/steampunk.png", "#FFD700", "#662200"),  # Gold text on brown background
    Theme("fantasy", "../assets/images/fantasy.png", "#00FF00", "#0B3B0B"),  # Green text on dark green background
    Theme("post-apocalyptic", "../assets/images/post-apocalyptic.png", "#C0C0C0", "#333333"),  # Silver text on dark gray background
]
# Add more themes here
