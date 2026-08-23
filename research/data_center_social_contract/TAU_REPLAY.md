# Tau Replay Status

## New packet

Specification: `tau/data_center_social_contract/data_center_admission_gate.tau`

Inputs: ten complete 1,024-row `sbf` streams.

Expected output: one accepted row, row 0; all ten single-fault rows and the remaining 1,013 rows reject.

## Static status

The packet generator and Python semantic checker pass. The spec is the same fail-closed conjunction pattern already used by the source-pinned compute-dividend and wealth gates.

## Native status

Native execution of this **new** packet is pending. The compute-dividend branch separately records actual candidate-native Tau execution for the existing V1.1, dividend, and wealth packets (16/256/256 rows, only row 0 accepted). That receipt does not automatically promote this new packet.

## Required promotion sequence

1. generate the packet deterministically;
2. bind spec, all inputs, expected output, generator, and checker hashes;
3. execute against the exact source-pinned candidate;
4. compare byte-for-byte with expected output;
5. replay against the reviewed binary identity;
6. record version, source/parser pins, binary hash, environment boundary, stdout/stderr, and exit code;
7. do not call the result Tau Net deployment, consensus, finality, oracle authentication, or settlement evidence.
