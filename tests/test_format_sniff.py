from polygraph.format_sniff import CheckpointFormat, sniff_format


def test_sniffs_real_safetensors_file(fixtures_dir):
    result = sniff_format(str(fixtures_dir / "safe_safetensors.bin"))
    assert result is CheckpointFormat.SAFETENSORS


def test_sniffs_real_pickle_file(fixtures_dir):
    result = sniff_format(str(fixtures_dir / "safe_pickle.pkl"))
    assert result is CheckpointFormat.PICKLE


def test_sniffs_malicious_pickle_as_pickle(fixtures_dir):
    # sniffing never executes anything -- confirms the malicious
    # fixture is still correctly identified as pickle-format by pure
    # byte inspection, same as a benign pickle.
    result = sniff_format(str(fixtures_dir / "malicious_pickle.pkl"))
    assert result is CheckpointFormat.PICKLE


def test_unknown_on_garbage_bytes(tmp_path):
    garbage = tmp_path / "garbage.bin"
    garbage.write_bytes(b"\xff\x00\xff\x00not a real format at all")
    result = sniff_format(str(garbage))
    assert result is CheckpointFormat.UNKNOWN
