#!/usr/bin/env bash
# Run inside a Linux/WSL filesystem, in the directory containing buildozer.spec.
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-17-openjdk-amd64}"
buildozer -v android debug
sha256sum bin/*.apk
