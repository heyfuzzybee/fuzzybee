#!/usr/bin/env bats

@test "fuzzybee-execute health exits 0" {
    run bash bin/fuzzybee-execute health
    [ "$status" -eq 0 ]
    [[ "$output" == *"HEALTHY"* ]]
}

@test "fuzzybee-execute decompose produces unit tree" {
    run bash bin/fuzzybee-execute decompose "bug: login crash on empty email"
    [ "$status" -eq 0 ]
    [[ "$output" == *"Reproduce"* ]]
    [[ "$output" == *"Root cause"* ]]
    [[ "$output" == *"Fix"* ]]
}

@test "fuzzybee-execute verify requires evidence" {
    run bash bin/fuzzybee-execute verify --task-id "nonexistent"
    [ "$status" -eq 1 ]
    [[ "$output" == *"not yet implemented"* ]]
}
