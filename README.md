![background](/templates/assets/images/background.jpg)

<div align="center">

# 🎴 HotImage
Easy-to-use application that turns folders into image API built from AlexFlipnote's [CoffeeAPI](https://github.com/AlexFlipnote/CoffeeAPI).

</div>

## Features
- API Documentation built-in
- Customizable start page
- File watcher that automatically uses changes to images and config

## Config
For a look into how you can customize your start page, make sure you rename `config.example.json` to `config.json` and look at the [Config Wiki](https://github.com/Snazzah/HotImage/wiki/Config).

To change the background of the start page, you can simply replace `templates/assets/images/background.jpg`.

## Limitations
- Cannot automatically switch ports upon config changing.
- Images with odd names may bug out the watcher and may require a restart.
- Images will not reload automattically when ignore patterns are changed.

## Sidenotes
If you want a simple single directory image API, check out [CoffeeAPI](https://github.com/AlexFlipnote/CoffeeAPI) instead.  
If you want to remove the example_coffee category, add `example_coffee` to the `ignore_patterns` array within the config.

## Screenshots
![screenshot1](https://get.snaz.in/9vewM1n.png)
![screenshot2](https://get.snaz.in/6P85egM.png)
![screenshot3](https://get.snaz.in/AdTewLq.png)

## Credits
- Website
  - [ModestaCSS](https://github.com/AlexFlipnote/ModestaCSS)
  - [smoothScroll](https://github.com/alicelieutier/smoothScroll)
  - [highlight.js](https://highlightjs.org/)
  - Adapted from [alexflipnote.github.io](https://github.com/AlexFlipnote/alexflipnote.github.io)'s style
- [Flask](https://pypi.org/project/Flask/)
- [watchdog](https://pypi.org/project/watchdog/)
