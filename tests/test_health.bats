#!/usr/bin/env bats

@test "fuzzybee-execute.sh health exits 0" {
    run bash scripts/fuzzybee-execute.sh health
    [ "$status" -eq 0 ]
    [[ "$output" == *"HEALTHY"* ]]
}

@test "fuzzybee-execute.sh decompose produces unit tree" {
    run bash scripts/fuzzybee-execute.sh decompose "bug: login crash on empty email"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Reproduce"* ]]
    [[ "$output" == *"Root Cause"* ]]
    [[ "$output" == *"Fix"* ]]
}

@test "fuzzybee-execute.sh verify requires evidence" {
    run bash scripts/fuzzybee-execute.sh verify --task-id "nonexistent"
    [ "$status" -eq 1 ]
    [[ "$output" == *"ERROR"* ]]
}
