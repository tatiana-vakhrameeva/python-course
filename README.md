### This repo contains python course homeworks

#### How to run:
* Install poetry (https://python-poetry.org/docs/#installation)
* Run ```./run init``` 

#### Lint
* Run ```poetry run flake8 [path]```

#### Code formatting
* Run ```poetry run black [path]```

#### Tests
* Run ```poetry run python -m unittest -v```

#### Log Analyzer
* Download jquery.tablesorter.min.js and put it to root project dir or specify path to it in template/report.html
* Run ```./run log_analyzer``` or ```./run log_analyzer --config CONFIG``` to pass config file

#### Run deco task
```./run deco```

#### Run poker task
```./run poker```

#### Run increment/decrement task
* Same steps as for until task