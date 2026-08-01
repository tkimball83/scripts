#!/usr/bin/env bash

function fail() {
  output "ERROR: ${1}" >&2
  exit 1
}

function output() {
  printf '[*]: %s\n' "${1}"
}

function output_command() {
  local -a command=("$@")
  local argument

  output "${command[0]} ${command[1]}"

  for argument in "${command[@]:2}"; do
    output "  ${argument}"
  done
}

function rclone_exec() {
  local trunk="${1}"
  local branch="${2}"
  local -a command

  command=("${RCLONE_BIN}" sync "${RCLONE_ARGS[@]}" "${trunk}" "${branch}")

  output_command "${command[@]}"
  echo

  "${command[@]}"
}

function require_command() {
  local command_path="${1}"

  if [[ "${command_path}" == */* ]]; then
    if [[ ! -x "${command_path}" ]]; then
      fail "Unable to execute ${command_path}."
    fi
  else
    if ! command -v "${command_path}" >/dev/null 2>&1; then
      fail "Unable to locate ${command_path}."
    fi
  fi
}

function require_file() {
  local file_path="${1}"

  [[ -f "${file_path}" ]] || fail "Unable to locate ${file_path}."
}

function resolve_rclone_config() {
  local config_path

  for config_path in "${RCLONE_CONFIG_PATHS[@]}"; do
    if [[ -f "${config_path}" ]]; then
      printf '%s\n' "${config_path}"
      return 0
    fi
  done

  return 1
}

function yaml_length() {
  local key="${1}"

  "${SHYAML_BIN}" get-length "${key}" <"${TREE_YAML}" 2>/dev/null
}

function yaml_value() {
  local key="${1}"

  "${SHYAML_BIN}" get-value "${key}" <"${TREE_YAML}" 2>/dev/null
}

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

while getopts "2b:c:df:k:l:s:t:" opt; do
  case $opt in
    2) enable_http2=true ;;
    b) rclone_bin=$OPTARG ;;
    c) rclone_config=$OPTARG ;;
    d) dry_run=true ;;
    f) tree_yaml=$OPTARG ;;
    k) rclone_checkers=$OPTARG ;;
    l) rclone_bwlimit=$OPTARG ;;
    s) shyaml_bin=$OPTARG ;;
    t) rclone_transfers=$OPTARG ;;
    *) exit 1 ;;
  esac
done

RCLONE_BIN=${rclone_bin-rclone}
RCLONE_BWLIMIT=${rclone_bwlimit-0}
RCLONE_CHECKERS=${rclone_checkers-32}
RCLONE_TRANSFERS=${rclone_transfers-16}
SHYAML_BIN=${shyaml_bin-shyaml}
TREE_YAML=${tree_yaml-"${SCRIPT_DIR}/tree.yaml"}
DRY_RUN=${dry_run-false}
ENABLE_HTTP2=${enable_http2-false}

declare -a RCLONE_CONFIG_PATHS=(
  "${HOME}/.config/rclone/rclone.conf"
  "/etc/rclone/rclone.conf"
)

if [[ -n "${rclone_config}" ]]; then
  RCLONE_CONFIG=${rclone_config}
else
  RCLONE_CONFIG=$(resolve_rclone_config) || fail "Unable to locate rclone config."
fi

require_command "${RCLONE_BIN}"
require_command "${SHYAML_BIN}"
require_file "${RCLONE_CONFIG}"
require_file "${TREE_YAML}"

declare -a RCLONE_ARGS=(
  "--bwlimit=${RCLONE_BWLIMIT}"
  "--checkers=${RCLONE_CHECKERS}"
  "--config=${RCLONE_CONFIG}"
  "--transfers=${RCLONE_TRANSFERS}"
)

[[ "${DRY_RUN}" = true ]] && RCLONE_ARGS+=(--dry-run)
[[ "${ENABLE_HTTP2}" = false ]] && RCLONE_ARGS+=(--disable-http2)

tree_length=$(yaml_length tree)

if [[ ! "${tree_length}" =~ ^[0-9]+$ ]] || ((tree_length <= 0)); then
  fail "The rclone tree list is empty."
fi

failures=0

for ((t = 0; t < tree_length; t++)); do

  trunk=$(yaml_value "tree.${t}.trunk")
  branch_length=$(yaml_length "tree.${t}.branches")

  if [[ -z "${trunk}" ]]; then
    output "WARNING: The rclone trunk is not defined, skipping." >&2
    continue
  fi

  if [[ ! "${branch_length}" =~ ^[0-9]+$ ]] || ((branch_length <= 0)); then
    output "WARNING: The rclone tree has no branches, skipping." >&2
    continue
  fi

  for ((b = 0; b < branch_length; b++)); do

    branch=$(yaml_value "tree.${t}.branches.${b}.name")
    leaf_length=$(yaml_length "tree.${t}.branches.${b}.leafs")

    if [[ -z "${branch}" ]]; then
      output "WARNING: The rclone branch has no name, skipping." >&2
      continue
    fi

    if [[ ! "${leaf_length}" =~ ^[0-9]+$ ]] || ((leaf_length <= 0)); then

      rclone_exec "${trunk}:" "${branch}:" || ((failures++))

    else
      for ((l = 0; l < leaf_length; l++)); do

        leaf=$(yaml_value "tree.${t}.branches.${b}.leafs.${l}")

        if [[ -z "${leaf}" ]]; then
          output "WARNING: The rclone leaf is not defined, skipping." >&2
          continue
        fi

        rclone_exec "${trunk}:${leaf}" "${branch}:${leaf}" || ((failures++))

      done
    fi
  done
done

if ((failures > 0)); then
  fail "${failures} rclone sync command(s) failed."
fi
