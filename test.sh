# Used for running tests from annother directory and without need of typing arguments again
# Simply run with path to this repo as parameter
# Or you can set parameter here by setting TEST_DIR on line below
TEST_DIR=.
# Specify if path to repo should be skipped and parase argument immediatly
ACCEPT_ARGUMENTS_ONLY=false
# You can specify default arguments here
ADDITIONAL_ARGUMENTS=
PYTHON_EXECUTABLE=python3
TESTER_NAME=test.py
APP_NAME=setcal
if $ACCEPT_ARGUMENTS_ONLY
then
	ADDITIONAL_ARGUMENTS=$@
else
	if [ $# -eq 0 ]
	then
		echo Running with default path $TEST_DIR
		echo Specify another directory with tests as first argument if you wish so
	elif [ $# -eq 1 ]
	then
		TEST_DIR=$1
	else
		shift
		ADDITIONAL_ARGUMENTS=$@
	fi
fi
CURRENT_PATH=$PWD
cd "$TEST_DIR"
RELATIVE_PATH=$(realpath --relative-to="." "$CURRENT_PATH")
$PYTHON_EXECUTABLE $TESTER_NAME $RELATIVE_PATH/$APP_NAME $ADDITIONAL_ARGUMENTS
