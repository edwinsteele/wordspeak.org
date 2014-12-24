#!/bin/sh


INCOMING_DIRECTORY="${HOME}/Dropbox/WordspeakIncoming";
DESTINATION_DIRECTORY="${HOME}/Code/wordspeak.org/posts";
FABRIC_EXECUTABLE="${HOME}/.virtualenvs/wordspeak_n7/bin/fab";
SLEEP_TIME_SECS=5;
LOGGING_FREQ_SECS=1000;

function send_pushover_message {
    curl -s \
        --form-string "token=${WORDSPEAK_PUSHOVER_API_TOKEN}" \
        --form-string "user=${WORDSPEAK_PUSHOVER_USER}" \
        --form-string "message=$1" \
        --form-string "title=$2" \
        https://api.pushover.net/1/messages.json > /dev/null
}

function validate_md_file {
    # Make sure there are the standard fields so we don't introduce a broken
    #  file into the repo
    # Inelegant, but effective, and rarely run so inefficiency isn't a biggie
    (grep "^.. description:" $1 &&
        grep "^.. tags:" $1 &&
        grep "^.. spellcheck_exceptions:" $1 &&
        grep "^.. date:" $1 &&
        grep "^.. title:" $1 &&
        grep "^.. slug:" $1;) > /dev/null
}

function do_log {
    # Don't clobber the builtin shell command, log
    echo "$(date): $@";
}

function possibly_log {
    # log this message at most once every LOGGING_FREQ_SECS, assuming this is
    #  only called once in every SLEEP_TIME_SECS
    if [ $(($(date +%s) % ${LOGGING_FREQ_SECS})) -gt $((${LOGGING_FREQ_SECS} - ${SLEEP_TIME_SECS})) ]; then
        do_log $@;
    fi
}

function do_deployment {
    # Deploy from the parent of the destination directory
    cd ${DESTINATION_DIRECTORY}/..;
    # Redirect dev null so that it doesn't think it's a simulated
    #  non-interactive deployment. This saves forcing this script to be run in
    #  a certain way.
    ${FABRIC_EXECUTABLE} non_interactive_deploy < /dev/null;
}

do_log "Starting automated deployment process for wordspeak";
while true; do
    incoming_md_files=$(find ${INCOMING_DIRECTORY} -name "*.md" -print);
    if [ -z "${incoming_md_files}" ]; then
        possibly_log "No files found. Sleeping";
    else
        for md_file in $(echo ${incoming_md_files}); do
            validate_md_file "${md_file}"
            if [ $? -eq 0 ]; then
                send_pushover_message "Deploying newly uploaded and valid file: ${md_file}" "Deploying new file"
                do_log "Deploying newly uploaded and valid file: ${md_file}"
                mv ${md_file} ${DESTINATION_DIRECTORY};
                do_deployment;
            else
                send_pushover_message "Deleting newly uploaded but invalid file: ${md_file}" "Deleting new file (invalid)"
                do_log "$(date): Deleting newly uploaded but invalid file ${md_file}";
                rm ${md_file};
            fi
        done
        do_log "Sleeping";
    fi
    sleep ${SLEEP_TIME_SECS};
done
