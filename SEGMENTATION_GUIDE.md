# Marking the phoneme boundaries

You do this twice, once for `q1_normal.wav` and once for `q2_whisper.wav`. Budget
about fifteen minutes each the first time.

## Which audio to open

Open the files in **`recordings_hp/`**, not `recordings/`.

Both folders hold the same recordings; the `_hp` copies have a 150 Hz high-pass applied that
removes the 100 Hz mains hum. The filter is zero-phase, so the two versions are sample-for-sample
aligned (checked: 0 samples of lag, identical durations). Boundaries you place on the filtered
file are therefore correct for the raw file as well.

It matters because the hum sits at almost exactly your F0. On the raw recording the bottom of
the spectrogram is a solid dark band, and Praat's pitch tracker locks onto the hum, so the pulse
display cannot be trusted. On the filtered copy the pulses follow the actual voicing, and the
pulses are the cue you rely on most for vowel onsets.

The analysis scripts still read the unfiltered recordings for energy and ZCR. That is handled
automatically and needs nothing from you.

One thing the filter costs you: the voice bar, the band of low-frequency energy during a voiced
stop closure, is removed along with the hum. It was not usable on the raw file anyway, since the
hum covered the same frequencies. Use the pulse display and the burst instead to tell /b/ and
/ɡ/ closures from /p/ and /k/.

## Opening the editor

1. In Praat, `Open > Read from file...` and select `recordings_hp/q1_normal.wav`.
2. `Open > Read from file...` again for `textgrids/q1_normal.TextGrid`.
3. Select **both** objects in the list (click one, ctrl-click the other), then `View & Edit`.

You get a window with the waveform on top, the spectrogram under it, and two tiers
below that: `phone` and `word`. All the labels are already typed. You only move boundaries.

## Set the spectrogram up first

This matters more than anything else. Under `Spectrum > Spectrogram settings...`:

- View range: **0 to 5000 Hz**
- Window length: **0.005 s**

That 5 ms window gives you a wideband spectrogram, where individual glottal pulses show
as vertical striations and the formants show as thick horizontal bands. That is what you
want for finding boundaries. A narrowband setting (0.03 s or longer) shows harmonics
instead and is much harder to segment from.

Also turn on `Pulses > Show pulses` and `Analyses > Show intensity`. The pulses tell you
where voicing is happening, which settles a lot of ambiguous cases.

## Moving a boundary

Click near the boundary in the tier, drag it. Praat snaps the cursor to zero crossings
if you have that enabled, which is helpful. Zoom with `Sel` / `In` / `Out` at the bottom
left, or select a region and hit `Zoom to selection`. Work zoomed in; at full-utterance
zoom everything looks approximately right and nothing is actually right.

Save with `File > Save TextGrid as text file...` back over `textgrids/q1_normal.TextGrid`.
Save as you go, not just at the end.

## What each boundary looks like

The sentence is `ð ə | b ɪ ɡ | p ɪ ɡ | s æ t | ɒ n | ə | θ ɪ k | ʃ iː t`.

**Silence to speech.** Put the first boundary where energy first rises out of the noise
floor. For `q1_normal.wav` that is the start of /ð/, which is weak, so look at the
spectrogram rather than the waveform, and look for low-frequency frication appearing.

**Stops (b, p, ɡ, k, t).** A stop has two visible parts. The closure is a near-silent gap,
often with a low-frequency voice bar along the bottom of the spectrogram if the stop is
voiced (b, ɡ). The release is a sharp vertical spike, the burst. Convention: start the
stop at the beginning of the closure, and end it at the onset of the following vowel's
voicing, not at the burst. The gap between burst and voicing onset is the aspiration, and
it belongs to the stop. This is exactly the VOT difference that separates /p/ from /b/,
so it is worth getting right in both recordings.

For the word-initial /b/ in "big" there may be no clear closure, since nothing precedes it
but silence. Start it where the voice bar or the burst begins.

**Fricatives (s, θ, ʃ, ð).** These are the easiest. Frication is a cloud of aperiodic
energy, and the onset and offset are usually sharp in the waveform envelope. The three of
them look different: /s/ is loud with energy concentrated high, above about 4 kHz; /ʃ/ is
loud with energy lower, around 2 to 4 kHz; /θ/ is noticeably quieter and more diffuse than
either, and its boundaries are correspondingly vaguer. /ð/ in "the" is weak and short and
may be partly voiced.

**Vowels (ə, ɪ, æ, ɒ, iː).** Start the vowel at the first glottal pulse, visible as the
first vertical striation and confirmed by the pulse markers. End it where the striations
stop or where the formants bend into the next consonant. When a formant transition is
gradual, the usual convention is to put the boundary where the formant leaves its steady
state.

**Nasal (n).** Voiced but much weaker than a vowel, with energy concentrated low and the
higher formants suddenly damped out. The boundary from /ɒ/ into /n/ shows as an abrupt
drop in overall intensity while the voicing striations continue.

**Word-final /t/ in "sheet".** It may be unreleased, in which case there is a closure and
then nothing. If there is no burst, end the /t/ where the energy has clearly gone.

## The whisper file

Same procedure, one difference: there is no voicing anywhere, so no striations and no
pulses. You lose the single most useful cue.

Work from the formants instead. Whispered vowels still have clear formant structure, it is
just excited by turbulent noise rather than glottal pulses, so it appears as bands in a
noisy background rather than bands crossed by striations. Vowel onsets and offsets are
mushier than in the normal recording. That is a real property of whispered speech, not a
mistake on your part, and it is worth remembering when you write up Q2, because the
difficulty you have segmenting it is itself evidence about what whispering removes.

Fricatives are relatively easier in the whisper file, since they were already aperiodic.

## When you're done

Run the checker on each file:

```sh
.venv/bin/python code/q1a_check_textgrid.py recordings/q1_normal.wav textgrids/q1_normal.TextGrid
```

It flags zero-width intervals, labels that got edited by accident, and durations that
suggest a boundary landed in the wrong place. It does not check whether your boundaries
are correct, only whether they are self-consistent. Tell me and I'll take a look too.
