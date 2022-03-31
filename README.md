### This repo contains python course homeworks

#### How to run:
* Install poetry (https://python-poetry.org/docs/#installation)
* Run ```./run init``` 

#### Log Analyzer
* Download jquery.tablesorter.min.js and put it to root project dir or specify path to it in template/report.html
* Run ```./run log_analyzer``` or ```./run log_analyzer --config CONFIG``` to pass config file
#### Lint
* Run ```poetry run flake8 [path]```

#### Code formatting
* Run ```poetry run black [path]```

#### Tests
* Run ```poetry run python -m unittest -v```

#### Run deco task
```./run deco```
