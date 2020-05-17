#!/bin/bash
red=31m
green=32m
yellow=33m
blue=34m
magenta=35m
cyan=36m
light_gray=37m
dark_gray=90m
light_red=91m
light_green=92m
light_yellow=93m
light_blue=94m
light_magenta=95m
light_cyan=96m
white=97m

print_color() {
  echo "\033[${1}${2}\033[0m"
}

if [ $ENVIRONMENT = "local" ]; then
  print_color $yellow "INITIALIZING DATABASE"
  airflow initdb
fi

print_color $yellow 'STARTING WEBSERVER IN BACKGROUND AND SCHEDULER IN FOREGROUND'
airflow webserver -D && airflow scheduler
