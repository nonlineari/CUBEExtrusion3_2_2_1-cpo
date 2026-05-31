import tempfile
import unittest
from pathlib import Path

from midi_to_metadata import convert_midi_file, parse_midi_bytes


def _vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("VLQ value must be non-negative.")
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append(0x80 | (value & 0x7F))
        value >>= 7
    out.reverse()
    return bytes(out)


def _build_minimal_midi() -> bytes:
    header = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big")
    header += (1).to_bytes(2, "big") + (480).to_bytes(2, "big")

    # Track: tempo 120 BPM, C4 note-on, note-off after 480 ticks, end-of-track.
    events = bytearray()
    events.extend(b"\x00\xff\x51\x03\x07\xa1\x20")  # Set tempo 500000 us/qn
    events.extend(b"\x00\x90\x3c\x64")  # Note on, note 60, velocity 100
    events.extend(_vlq(480))
    events.extend(b"\x80\x3c\x40")  # Note off, note 60
    events.extend(b"\x00\xff\x2f\x00")  # End of track

    track = b"MTrk" + len(events).to_bytes(4, "big") + bytes(events)
    return header + track


class MidiToMetadataTests(unittest.TestCase):
    def test_parse_midi_bytes_returns_expected_summary(self) -> None:
        metadata = parse_midi_bytes(_build_minimal_midi())

        self.assertEqual(metadata["format_type"], 0)
        self.assertEqual(metadata["track_count"], 1)
        self.assertEqual(metadata["ticks_per_quarter_note"], 480)
        self.assertEqual(metadata["total_ticks"], 480)
        self.assertAlmostEqual(metadata["estimated_duration_seconds"], 0.5, places=6)
        self.assertEqual(metadata["total_events"], 4)

        track = metadata["tracks"][0]
        self.assertEqual(track["note_on_events"], 1)
        self.assertEqual(track["note_off_events"], 1)
        self.assertEqual(track["notes_completed"], 1)
        self.assertEqual(track["note_histogram"]["60"], 1)
        self.assertEqual(track["note_duration_ticks"]["average"], 480.0)

    def test_parse_midi_bytes_includes_notes_when_requested(self) -> None:
        metadata = parse_midi_bytes(_build_minimal_midi(), include_notes=True)
        notes = metadata["tracks"][0]["notes"]

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["channel"], 0)
        self.assertEqual(notes[0]["note"], 60)
        self.assertEqual(notes[0]["duration_ticks"], 480)

    def test_convert_midi_file_can_replace_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            midi_path = Path(tmpdir) / "example.mid"
            output_path = Path(tmpdir) / "example.metadata.json"

            midi_path.write_bytes(_build_minimal_midi())
            written_path, metadata = convert_midi_file(
                midi_path, output_path=output_path, replace_source=True
            )

            self.assertEqual(written_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertFalse(midi_path.exists())
            self.assertEqual(metadata["source_midi"], "example.mid")


if __name__ == "__main__":
    unittest.main()
