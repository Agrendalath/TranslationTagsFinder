# Translation Tags Finder

This is a small script to find tags like:
```
"{{"Test string" | translate}}"
```

in repositories.

## Dependencies
In order to use this script you need to install [The Silver Searcher](https://github.com/ggreer/the_silver_searcher).

## Usage
You can run it with:
```
python3 finder.py -p /path/to/code -l /path/to/locales/directory
```