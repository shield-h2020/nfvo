#!/bin/bash

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

copy_conf() {
    # copy configuration sample files
    for conf in conf/*conf.sample
    do
	conf_name=${conf%.sample}
	if [ ! -f $conf_name ]; then
            cp $conf $conf_name
	fi
    done
}

generate_certs() {
    # Generate certs and keys
    cd bin/
    ./gen_creds.sh
    cd ..
}

setup() {
    # Prepare host virtualenv (docker-compose)
    rm -rf venv
    virtualenv venv -p python3
    source venv/bin/activate
    pip install --upgrade pip setuptools
    pip install docker-compose jinja2

    # Render docker configuration
    python docker/configure.py

    # Start docker compose
    docker-compose -f docker/docker-compose.yml up -d --force-recreate
}

test() {
    # Perform tests on the same nfvo container
    docker exec -t -i docker_nfvo_1 "/bin/bash" -c "python test/main.py"
}

parse_options "$@"

# Copy configuration sample files
copy_conf

# Install dependencies
generate_certs

# Set-up env (pre-requirements)
setup

if [[ $p_test == true ]]; then
    echo "Waiting for nfvo ..."
    until nc -z localhost 8448
    do
	echo "."
	sleep 1
    done
    test
fi
