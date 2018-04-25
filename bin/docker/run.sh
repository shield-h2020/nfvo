#/bin/bash

# Based on SHIELD's Store deployment script

param_not_set() {
      echo "Parameter not set: $1"
      usage
      exit 1
}

param_invalid() {
      echo "Value not allowed for parameter: $1"
      usage
      exit 1
}

usage()
{
    cat <<USAGE_MSG
USAGE: $0 OPTIONS
Sets up the docker environment and starts up all daemons. Configuration is retrieved from the .env* files

OPTIONS
   --test               (Optional) Execute the tests against the vNSFO
   --teardown           (Optional) Stops all vNSFO-related running containers
   -h                   Prints this usage message
USAGE_MSG
}

parse_options() {

    parse_cmd=`getopt -n$0 -o h:: -a --long test,teardown -- "$@"`
    if [ $? != 0 ] ; then
	usage
	echo
	echo
	exit 1
    fi

    eval set -- "$parse_cmd"

    [ $# -eq 0 ] && usage

    while [ $# -gt 0 ]
    do
	case "$1" in

	    --test)
		p_test=true
		;;

	    --teardown)
		p_teardown=true
		;;

	    -h)
		usage
		exit 1
		;;

	    # End marker from getopt
	     --)
		shift
		break
		;;

	    -*)
		echo "Unknown option $1"
		usage
		exit 1
		;;

	    *)
		# Any additional parameter is an error.
		echo "Too many parameters provided."
		Usage
		exit 1
		;;

	esac
	shift
    done

    return $OPTIND
}

_PARAM_INVALID_VALUE="__##_INVALID_VALUE_##__"

p_test=$_PARAM_INVALID_VALUE
p_teardown=$_PARAM_INVALID_VALUE

header() {
  bg="e[0;46m"
  nc="e[0m"
  text=$(echo $1 | awk '{print toupper($0)}')
  echo -e "\\${bg}$text\\${nc}\n"
}

cleanup()
{
    rm -f ${ENV_FILE_FULL}
    rm -f ${ENV_TMP_FILE}
    rm -f ${DOCKER_COMPOSE_FILE}
    rm -f ${DOCKER_FILE_NFVO}
    rm -f ${DOCKER_FILE_DB}
    rm -f ${DOCKER_FILE_TEST}
}

teardown() {
    header "Tearing down all ${CNTR_PROJECT}-related Docker containers"
    # Stop and remove containers
    containers=($($DOCKER ps -aq --filter label=project\=${CNTR_PROJECT}))
    $DOCKER stop "${containers[@]}"
    $DOCKER rm "${containers[@]}"
    return 0
}

deps() {
    sudo apt-get install python3 python3-pip -y
    # Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-get update
    sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable"
    sudo apt-get install docker-ce=17.09.1~ce-0~ubuntu
    sudo usermod -G docker $(whoami)
    sudo pip3 install docker-compose==1.17.1
}

setup() {
    current=$PWD
    cd ..
    # Generate server credentials
    ./gen_creds.sh
    # Set-up conf files
    ./set_conf.sh
    cd ${current}
}

# ===

# Parse options provided to script
parse_options "$@"

if [[ $p_teardown != true ]]; then
    # Install dependencies
    deps

    # Set-up env (pre-requirements)
    setup
fi

# The environment variables start off with the one from the production environment and get replaced from there
ENV_FILE_FULL=$(mktemp /tmp/XXXXXXX)

# Append settings for standard operation
cat .env.base >> ${ENV_FILE_FULL}
cat .env.production >> ${ENV_FILE_FULL}

. ${ENV_FILE_FULL}

# Export variables so they can be used here. Stop script at first error
set -ae

# Do nested variables interpolation as the shell doesn't seem do it
ENV_FILE=$(mktemp /tmp/XXXXXXX)
ENV_TMP_FILE=$(mktemp /tmp/XXXXXXX)
echo "#!/bin/sh" > ${ENV_TMP_FILE}
echo ". ${ENV_FILE_FULL}" >> ${ENV_TMP_FILE}
echo "cat <<_VARS_BLOCK_" >> ${ENV_TMP_FILE}
cat ${ENV_FILE_FULL} >> ${ENV_TMP_FILE}
echo "_VARS_BLOCK_" >> ${ENV_TMP_FILE}
echo >> ${ENV_TMP_FILE}
. ${ENV_TMP_FILE} > ${ENV_FILE}

# Tools
DOCKER=$(command -v docker || { echo "Error: No docker found." >&2; cleanup; exit 1; })
DOCKER_COMPOSE=$(command -v docker-compose || { echo "Error: No docker-compose found." >&2; cleanup; exit 1; })

if [[ $p_teardown = true ]]; then
    teardown
    exit 0
fi

header "Setting up ${CNTR_PROJECT}-related Docker containers"

# Remove the template extension from files
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE_TEMPLATE%.*}"
DOCKER_FILE_NFVO="${DOCKER_FILE_TEMPLATE_NFVO%.*}"
DOCKER_FILE_DB="${DOCKER_FILE_TEMPLATE_DB%.*}"

# Replace variables
envsubst < ${DOCKER_COMPOSE_FILE_TEMPLATE} > ${DOCKER_COMPOSE_FILE}
envsubst < ${DOCKER_FILE_TEMPLATE_NFVO} > ${DOCKER_FILE_NFVO}

COMPOSE_FILES="-f ${DOCKER_COMPOSE_FILE}"

if [[ $p_test = true ]]; then
    DOCKER_COMPOSE_FILE_TEST="${DOCKER_COMPOSE_FILE_TEST_TEMPLATE%.*}"
    DOCKER_FILE_TEST="${DOCKER_FILE_TEMPLATE_TEST%.*}"
    envsubst < ${DOCKER_COMPOSE_FILE_TEST_TEMPLATE} > ${DOCKER_COMPOSE_FILE_TEST}
    envsubst < ${DOCKER_FILE_TEMPLATE_TEST} > ${DOCKER_FILE_TEST}
    COMPOSE_FILES="-${COMPOSE_FILES} -f ${DOCKER_COMPOSE_FILE_TEST}"
fi

# Set containers prefix
COMPOSE_PROJECT_NAME=${PROJECT}

# Create services
echo "${DOCKER_COMPOSE} ${COMPOSE_FILES} build --force-rm"
${DOCKER_COMPOSE} ${COMPOSE_FILES} build --force-rm

# Run containers as daemons
COMPOSE_FLAGS=-d

# Loadup containers
echo "${DOCKER_COMPOSE} ${COMPOSE_FILES} up ${COMPOSE_FLAGS}"
${DOCKER_COMPOSE} ${COMPOSE_FILES} up ${COMPOSE_FLAGS}

echo "Containers set-up finished successfully"

if [[ $p_test = true ]]; then
    REPORT_PATH=$(mktemp -d /tmp/nfvo-test_XXXXXXX)
    REPORT_FULL_PATH=$REPORT_PATH/report.log
    max=50

    echo -e "\n\n"
    header "Waiting for tests to finish"
    echo "Logs will be copied to $REPORT_FULL_PATH"
    docker_log_cmd="docker logs docker_nfvo-test_1 >& ${REPORT_PATH}/report.log"
    while true; do
	 if [[ $(sudo docker ps -a | grep nfvo-test) == *"Exited"* ]]; then
	    docker logs docker_nfvo-test_1 >& ${REPORT_PATH}/report.log
	    echo "Testing finished. Logs copied"
	    exit "0"
	fi
	max=$((max-1))
	if [[ $max -eq 0 ]]; then
	    echo "Timeout. Exiting without copying logs"
	    echo "Once tests are finished (check in \"docker ps -a\"), run the command \"$docker_log_cmd\""
	    exit 0
	fi
	sleep 5
    done
fi

cleanup

echo -e "\n\n"
