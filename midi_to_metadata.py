#!/usr/bin/env python3
"""Convert MIDI files to compact JSON metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class MidiParseError(ValueError):
    """Raised when the MIDI stream is malformed or unsupported."""


def _read_u16_be(data: bytes, offset: int) -> Tuple[int, int]:
    if offset + 2 > len(data):
        raise MidiParseError("Unexpected end of stream while reading uint16.")
    return int.from_bytes(data[offset : offset + 2], "big"), offset + 2


def _read_u32_be(data: bytes, offset: int) -> Tuple[int, int]:
    if offset + 4 > len(data):
        raise MidiParseError("Unexpected end of stream while reading uint32.")
    return int.from_bytes(data[offset : offset + 4], "big"), offset + 4


def _read_variable_length_quantity(data: bytes, offset: int) -> Tuple[int, int]:
    value = 0
    start = offset
    for _ in range(4):
        if offset >= len(data):
            raise MidiParseError("Unexpected end of stream while reading VLQ.")
        current = data[offset]
        offset += 1
        value = (value << 7) | (current & 0x7F)
        if current < 0x80:
            return value, offset
    raise MidiParseError(f"Invalid VLQ at offset {start}: exceeds 4 bytes.")


def _decode_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _tempo_to_bpm(microseconds_per_quarter: int) -> float:
    if microseconds_per_quarter <= 0:
        return 0.0
    return 60_000_000.0 / float(microseconds_per_quarter)


def _ticks_to_seconds(
    total_ticks: int, ticks_per_quarter: int, tempo_changes: Sequence[Tuple[int, int]]
) -> float:
    if total_ticks <= 0 or ticks_per_quarter <= 0:
        return 0.0

    changes = sorted(tempo_changes, key=lambda item: item[0])
    if not changes or changes[0][0] > 0:
        changes = [(0, 500_000)] + list(changes)

    seconds = 0.0
    current_tick = 0
    current_tempo = 500_000

    for tick, tempo in changes:
        if tick <= current_tick:
            current_tempo = tempo
            continue
        delta_ticks = min(tick, total_ticks) - current_tick
        if delta_ticks > 0:
            seconds += (delta_ticks * current_tempo) / (
                ticks_per_quarter * 1_000_000.0
            )
            current_tick += delta_ticks
        if current_tick >= total_ticks:
            return seconds
        current_tempo = tempo

    if current_tick < total_ticks:
        delta_ticks = total_ticks - current_tick
        seconds += (delta_ticks * current_tempo) / (ticks_per_quarter * 1_000_000.0)

    return seconds


def _parse_track(
    track_data: bytes,
    track_index: int,
    include_notes: bool,
    max_text_events: int,
) -> Tuple[Dict[str, Any], List[Tuple[int, int]], int]:
    offset = 0
    absolute_tick = 0
    running_status: Optional[int] = None
    tempo_changes: List[Tuple[int, int]] = []

    notes_open: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    note_histogram: Dict[str, int] = {}
    note_events: List[Dict[str, int]] = []
    completed_note_durations: List[int] = []
    channels = set()

    summary: Dict[str, Any] = {
        "track_index": track_index,
        "events": 0,
        "channel_events": 0,
        "meta_events": 0,
        "sysex_events": 0,
        "note_on_events": 0,
        "note_off_events": 0,
        "notes_completed": 0,
        "program_changes": 0,
        "control_changes": 0,
        "pitch_bends": 0,
        "channel_pressures": 0,
        "polyphonic_pressures": 0,
        "tempo_changes": [],
        "time_signatures": [],
        "key_signatures": [],
        "text_events": [],
        "meta_event_type_counts": {},
        "note_histogram": note_histogram,
    }

    while offset < len(track_data):
        delta, offset = _read_variable_length_quantity(track_data, offset)
        absolute_tick += delta

        if offset >= len(track_data):
            raise MidiParseError("Unexpected end of track data after delta-time.")

        status = track_data[offset]
        if status < 0x80:
            if running_status is None:
                raise MidiParseError(
                    f"Running status used without prior status in track {track_index}."
                )
            status = running_status
        else:
            offset += 1
            if status < 0xF0:
                running_status = status

        summary["events"] += 1

        if status == 0xFF:
            summary["meta_events"] += 1
            if offset >= len(track_data):
                raise MidiParseError("Meta event missing event type.")
            meta_type = track_data[offset]
            offset += 1
            length, offset = _read_variable_length_quantity(track_data, offset)
            if offset + length > len(track_data):
                raise MidiParseError("Meta event extends beyond track bounds.")
            payload = track_data[offset : offset + length]
            offset += length

            key = f"0x{meta_type:02X}"
            summary["meta_event_type_counts"][key] = (
                summary["meta_event_type_counts"].get(key, 0) + 1
            )

            if meta_type == 0x51 and length == 3:
                tempo_us_qn = int.from_bytes(payload, "big")
                tempo_changes.append((absolute_tick, tempo_us_qn))
                summary["tempo_changes"].append(
                    {
                        "tick": absolute_tick,
                        "microseconds_per_quarter_note": tempo_us_qn,
                        "bpm": round(_tempo_to_bpm(tempo_us_qn), 6),
                    }
                )
            elif meta_type == 0x58 and length == 4:
                numerator = payload[0]
                denominator = 2 ** payload[1]
                summary["time_signatures"].append(
                    {
                        "tick": absolute_tick,
                        "numerator": numerator,
                        "denominator": denominator,
                    }
                )
            elif meta_type == 0x59 and length == 2:
                summary["key_signatures"].append(
                    {
                        "tick": absolute_tick,
                        "sharps_flats": int.from_bytes(
                            payload[:1], "big", signed=True
                        ),
                        "mode": "minor" if payload[1] else "major",
                    }
                )
            elif 0x01 <= meta_type <= 0x07 and len(summary["text_events"]) < max_text_events:
                summary["text_events"].append(
                    {
                        "tick": absolute_tick,
                        "type": key,
                        "text": _decode_text(payload),
                    }
                )

            if meta_type == 0x2F:
                break
            continue

        if status in (0xF0, 0xF7):
            summary["sysex_events"] += 1
            length, offset = _read_variable_length_quantity(track_data, offset)
            if offset + length > len(track_data):
                raise MidiParseError("SysEx event extends beyond track bounds.")
            offset += length
            continue

        event_type = status >> 4
        channel = status & 0x0F
        channels.add(channel)
        summary["channel_events"] += 1

        if event_type in (0x8, 0x9, 0xA, 0xB, 0xE):
            if offset + 2 > len(track_data):
                raise MidiParseError("Channel event missing data bytes.")
            data1 = track_data[offset]
            data2 = track_data[offset + 1]
            offset += 2
        elif event_type in (0xC, 0xD):
            if offset >= len(track_data):
                raise MidiParseError("Channel event missing data byte.")
            data1 = track_data[offset]
            data2 = None
            offset += 1
        else:
            raise MidiParseError(
                f"Unsupported MIDI channel event type 0x{event_type:X} in track {track_index}."
            )

        if event_type == 0x8:
            summary["note_off_events"] += 1
            note_key = (channel, data1)
            starts = notes_open.get(note_key, [])
            if starts:
                start_tick, velocity = starts.pop()
                duration_ticks = max(0, absolute_tick - start_tick)
                summary["notes_completed"] += 1
                completed_note_durations.append(duration_ticks)
                if include_notes:
                    note_events.append(
                        {
                            "channel": channel,
                            "note": data1,
                            "velocity": velocity,
                            "start_tick": start_tick,
                            "end_tick": absolute_tick,
                            "duration_ticks": duration_ticks,
                        }
                    )
                if not starts:
                    notes_open.pop(note_key, None)
        elif event_type == 0x9:
            if data2 == 0:
                summary["note_off_events"] += 1
                note_key = (channel, data1)
                starts = notes_open.get(note_key, [])
                if starts:
                    start_tick, velocity = starts.pop()
                    duration_ticks = max(0, absolute_tick - start_tick)
                    summary["notes_completed"] += 1
                    completed_note_durations.append(duration_ticks)
                    if include_notes:
                        note_events.append(
                            {
                                "channel": channel,
                                "note": data1,
                                "velocity": velocity,
                                "start_tick": start_tick,
                                "end_tick": absolute_tick,
                                "duration_ticks": duration_ticks,
                            }
                        )
                    if not starts:
                        notes_open.pop(note_key, None)
            else:
                summary["note_on_events"] += 1
                note_name = str(data1)
                note_histogram[note_name] = note_histogram.get(note_name, 0) + 1
                notes_open.setdefault((channel, data1), []).append((absolute_tick, data2))
        elif event_type == 0xA:
            summary["polyphonic_pressures"] += 1
        elif event_type == 0xB:
            summary["control_changes"] += 1
        elif event_type == 0xC:
            summary["program_changes"] += 1
        elif event_type == 0xD:
            summary["channel_pressures"] += 1
        elif event_type == 0xE:
            summary["pitch_bends"] += 1

    summary["channels"] = sorted(channels)
    summary["open_notes"] = sum(len(starts) for starts in notes_open.values())
    if completed_note_durations:
        summary["note_duration_ticks"] = {
            "min": min(completed_note_durations),
            "max": max(completed_note_durations),
            "average": round(
                sum(completed_note_durations) / float(len(completed_note_durations)), 6
            ),
        }
    else:
        summary["note_duration_ticks"] = {"min": 0, "max": 0, "average": 0.0}

    if include_notes:
        summary["notes"] = note_events

    return summary, tempo_changes, absolute_tick


def parse_midi_bytes(
    data: bytes, *, source_name: str = "in-memory", include_notes: bool = False, max_text_events: int = 8
) -> Dict[str, Any]:
    offset = 0
    if len(data) < 14:
        raise MidiParseError("Input is too short to be a valid MIDI file.")

    if data[offset : offset + 4] != b"MThd":
        raise MidiParseError("Missing MIDI header chunk (MThd).")
    offset += 4

    header_length, offset = _read_u32_be(data, offset)
    if header_length < 6:
        raise MidiParseError(f"Invalid MIDI header length: {header_length}.")
    if offset + header_length > len(data):
        raise MidiParseError("MIDI header exceeds file size.")

    format_type, header_offset = _read_u16_be(data, offset)
    track_count, header_offset = _read_u16_be(data, header_offset)
    division, header_offset = _read_u16_be(data, header_offset)
    offset += header_length

    if division & 0x8000:
        raise MidiParseError(
            "SMPTE time division is not supported; use PPQ-based MIDI files."
        )

    ticks_per_quarter = division
    tracks: List[Dict[str, Any]] = []
    tempo_changes: List[Tuple[int, int]] = []
    total_ticks = 0
    total_events = 0

    for track_index in range(track_count):
        if offset + 8 > len(data):
            raise MidiParseError("Unexpected end of stream while reading track header.")
        if data[offset : offset + 4] != b"MTrk":
            raise MidiParseError(f"Missing MTrk header for track {track_index}.")
        offset += 4

        track_length, offset = _read_u32_be(data, offset)
        if offset + track_length > len(data):
            raise MidiParseError(f"Track {track_index} extends beyond file size.")
        track_data = data[offset : offset + track_length]
        offset += track_length

        summary, track_tempos, track_ticks = _parse_track(
            track_data,
            track_index,
            include_notes=include_notes,
            max_text_events=max_text_events,
        )
        tracks.append(summary)
        tempo_changes.extend(track_tempos)
        total_ticks = max(total_ticks, track_ticks)
        total_events += int(summary["events"])

    estimated_duration_seconds = _ticks_to_seconds(
        total_ticks=total_ticks,
        ticks_per_quarter=ticks_per_quarter,
        tempo_changes=tempo_changes,
    )

    tempo_map = [
        {
            "tick": tick,
            "microseconds_per_quarter_note": tempo,
            "bpm": round(_tempo_to_bpm(tempo), 6),
        }
        for tick, tempo in sorted(tempo_changes, key=lambda item: item[0])
    ]
    if not tempo_map:
        tempo_map = [
            {
                "tick": 0,
                "microseconds_per_quarter_note": 500_000,
                "bpm": 120.0,
            }
        ]

    return {
        "source_midi": source_name,
        "format_type": format_type,
        "track_count": track_count,
        "ticks_per_quarter_note": ticks_per_quarter,
        "total_ticks": total_ticks,
        "estimated_duration_seconds": round(estimated_duration_seconds, 6),
        "total_events": total_events,
        "tempo_map": tempo_map,
        "tracks": tracks,
        "converter": {
            "name": "midi_to_metadata",
            "version": 1,
            "notes_included": include_notes,
            "max_text_events_per_track": max_text_events,
        },
    }


def parse_midi_file(
    input_path: Path, *, include_notes: bool = False, max_text_events: int = 8
) -> Dict[str, Any]:
    raw = input_path.read_bytes()
    return parse_midi_bytes(
        raw,
        source_name=input_path.name,
        include_notes=include_notes,
        max_text_events=max_text_events,
    )


def convert_midi_file(
    input_path: Path,
    output_path: Optional[Path] = None,
    *,
    include_notes: bool = False,
    max_text_events: int = 8,
    indent: Optional[int] = 2,
    replace_source: bool = False,
) -> Tuple[Path, Dict[str, Any]]:
    metadata = parse_midi_file(
        input_path,
        include_notes=include_notes,
        max_text_events=max_text_events,
    )
    final_output = output_path or input_path.with_suffix(".metadata.json")
    final_output.write_text(json.dumps(metadata, indent=indent) + "\n", encoding="utf-8")

    if replace_source:
        if final_output.resolve() == input_path.resolve():
            raise ValueError("Output path must differ from input when --replace is used.")
        input_path.unlink()

    return final_output, metadata


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a MIDI file into compact JSON metadata."
    )
    parser.add_argument("input_midi", type=Path, help="Path to the input .mid file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: <input>.metadata.json)",
    )
    parser.add_argument(
        "--include-notes",
        action="store_true",
        help="Include individual completed note events in output metadata",
    )
    parser.add_argument(
        "--max-text-events",
        type=int,
        default=8,
        help="Maximum number of text meta events kept per track",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete the original MIDI file after successful conversion",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation width (use 0 for compact output)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.max_text_events < 0:
        parser.error("--max-text-events must be >= 0.")

    if not args.input_midi.exists():
        parser.error(f"Input file does not exist: {args.input_midi}")

    try:
        output_path, metadata = convert_midi_file(
            args.input_midi,
            output_path=args.output,
            include_notes=args.include_notes,
            max_text_events=args.max_text_events,
            indent=(None if args.indent <= 0 else args.indent),
            replace_source=args.replace,
        )
    except (MidiParseError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Converted '{args.input_midi}' to '{output_path}' "
        f"({metadata['total_events']} events, {metadata['estimated_duration_seconds']}s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
