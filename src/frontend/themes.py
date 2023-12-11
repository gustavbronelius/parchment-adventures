# File: themes.py

class Theme:
    def __init__(self, name, background_image, text_color, console_bg_color):
        self.name = name
        self.background_image = background_image
        self.text_color = text_color
        self.console_bg_color = console_bg_color

# Themes are now defined as a list
themes_list = [
    Theme("light", "../assets/images/scroll.png", "black", "white"),
    Theme("dark", "../assets/images/scroll.png", "white", "black"),
    Theme("horror", "../assets/images/horror.png", "#E6E6FA", "#1C1C1C"),
    Theme("sci-fi", "../assets/images/scifi.png", "#00FFFF", "#00008B"),
    Theme("cyberpunk", "../assets/images/cyberpunk_background.png", "#FF1493", "#8B008B"),
    Theme("mystery", "../assets/images/adventure.png", "#DAA520", "#800000"),
    Theme("steampunk", "../assets/images/steampunk_background.png", "#B8860B", "#A52A2A"),
    Theme("fantasy", "../assets/images/fantasy_background.png", "#0000CD", "#FFF8DC"),
    Theme("post-apocalyptic", "../assets/images/post_apocalyptic_background.png", "#B22222", "#808080"),
    # Add more themes here
]