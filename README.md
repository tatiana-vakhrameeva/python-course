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

#### Run opcode task
* Run cpython in docker ```docker run -ti --rm -v [your-path-to-project]/hw2:/tmp/bin centos /bin/bash```
* Run ```./tmp/bin/init``` to install and compile cpython
* Change directory ```cd opt/cpython``` and apply git patch ```git apply ../../tmp/bin/new_opcode.patch```

