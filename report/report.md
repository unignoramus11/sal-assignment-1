---
title: "Speech Analysis and Linguistics: Assignment 1"
author: "Mohit Singh (2023111021)"
mainfont: "Charis"
fontsize: 11pt
geometry: margin=1in
linkcolor: black
urlcolor: black
header-includes:
  - \usepackage{float}
  - \usepackage{booktabs}
  - \setlength{\emergencystretch}{3em}
---

# Method

Recordings were made in Praat 7.0, mono at 44.1 kHz, at a fixed microphone distance across
all takes. Recording was done under a duvet to damp room reflections.

![Recording setup.](me_recording.jpg){width=55%}

Short-time energy and ZCR (Q1) were computed in NumPy with a 20 ms Hamming window and 10 ms
shift, which at 44.1 kHz is an 882-sample window advancing 441 samples. Pitch (Q5) and
formants (Q4) were extracted with Praat. Phoneme boundaries (Q1a, Q2) were marked by hand in
Praat from the waveform and a wideband spectrogram (5 ms window, 0–5 kHz) with glottal
pulses shown: stops begin at the onset of closure and the following vowel at the first
glottal pulse, fricatives at the onset of frication.

**Mains interference.** All recordings contain a steady 100.0 Hz component, the second
harmonic of the 50 Hz supply, present in the silences as well as during speech. Since the
speaker's F0 is near 100 Hz, this falls inside the pitch search range. On the raw signal the
whispered file appears to have 18.8% voiced frames, but the proportion is the same inside
the speech region (18.4%) as outside it (22.6%), whereas the normal file gives 73.8% against
4.7%; and the 80–130 Hz band rises only 3.5 dB from silence to speech in the whisper against
31 dB in the 2–5 kHz band. The component does not follow the speech, so it comes from the
mains supply. A 4th-order high-pass at 150 Hz removes it (−27 dB). Autocorrelation pitch tracking is
unaffected by losing the fundamental, since the period is unchanged. Pitch and formants were
measured on the filtered signals; energy and ZCR were measured on the unfiltered recordings.

Everything regenerates with `code/run_all.sh`.

\newpage

# Question 3

**(a) "reusable" = "re-" + "use" + "-able".** Morphology: the internal structure of a word
and how its parts combine. Two derivational affixes attach to a free root, and the order is
[[re + use] + able].

**(b) "bank" as riverside or financial institution.** Semantics: the relation between a form
and its meanings. This is homonymy rather than polysemy, as the river sense comes through
Old Norse and the financial sense through Italian *banca*, so they are two distinct lexical
items sharing a form.

**(c) "The teacher explained the lesson to the students" is SVO.** Syntax: the arrangement
of constituents and the word order English uses. It does not depend on what the words mean.

**(d) "fan" and "van" differ by one phoneme.** Phonology: the minimal-pair test establishes
that /f/ and /v/ are contrastive phonemes of English. Phonetics would describe how they
differ physically (both labiodental fricatives, /v/ voiced); phonology concerns the fact
that the difference distinguishes words. The same phonetic difference is not contrastive in
every language.

**(e) "It's getting dark in here" as a request.** Pragmatics: the literal content is a
statement, the intended force is a request. This is an indirect speech act, resolved by
reasoning about context. Nothing in the words encodes a request.

**(f) [t] in "talk" made with the tongue behind the upper front teeth.** Phonetics,
specifically articulatory. The description is inaccurate for standard English: /t/ is
**alveolar**, with the tongue tip at the alveolar ridge, not at the teeth. Dental [t̪] does
occur in English before a dental fricative ("eighth") and in several varieties including
many Indian English accents, but not in "talk".

\newpage

# Question 4

"beat" and "bit" were recorded in isolation at matched loudness and pitch. Formants were
extracted with Praat's Burg method (5 poles, 5500 Hz maximum, 25 ms window). The vowel was
taken as the longest run within 10 dB of peak energy in a 300–3500 Hz band, and values are
averaged over the middle third of that region.

| | vowel | duration (ms) | F1 (Hz) | F2 (Hz) | F3 (Hz) | F2 − F1 (Hz) |
|---|---|---|---|---|---|---|
| beat | /iː/ | 187.5 | 298 | 2591 | 2833 | 2293 |
| bit | /ɪ/ | 93.7 | 467 | 1901 | 2564 | 1434 |

![Formant tracks with the measured vowel region shaded, and the two vowels in the F1/F2 plane](../plots/q4_formants.png)

Differences observed:

- **F1 is 169 Hz higher in "bit".** F1 varies inversely with tongue height, so /ɪ/ has a
  lower tongue body. /iː/ is close, /ɪ/ near-close.
- **F2 is 690 Hz lower in "bit".** F2 rises as the tongue moves forward, so /iː/ is fully
  front and /ɪ/ is retracted towards the centre.
- **F2 − F1** is 2293 Hz for /iː/ and 1434 Hz for /ɪ/. This combines both effects and gives
  a larger difference than either formant on its own.
- **F3 is similar** (2833 vs 2564 Hz), as expected since F3 depends less on height and
  frontness. In "beat" F2 and F3 converge to within 240 Hz, characteristic of a close front
  vowel.
- **The vowel in "beat" is twice as long.** /iː/ is tense and /ɪ/ lax. The ratio is larger
  than the usual 1.5:1 because these are isolated words with no following material.

F2 in "beat" rises through the vowel rather than holding flat, which is the offglide of the
diphthongised English /iː/.

The result depends on the maximum-formant setting. At 5000 Hz the tracker gave F2 = 1716 Hz
for "beat", lower than for "bit" and contradicting the spectrogram, where the second formant
is clearly near 2600 Hz. At 5500 Hz it follows the visible bands correctly for both words.

\newpage

# Question 5

"Did you miss the exam?" was recorded neutrally as a baseline and in four emotions. Pitch was
extracted in Praat with `To Pitch` at a 10 ms step, floor 70 Hz, ceiling 500 Hz. Frames
outside the speech region and voiced runs shorter than three frames were discarded.

| emotion | duration (s) | mean F0 (Hz) | min | max | range (Hz) | range (st) | SD (Hz) |
|---|---|---|---|---|---|---|---|
| neutral | 1.76 | 110.2 | 96.2 | 119.7 | 23.5 | 3.78 | 5.4 |
| happy | 1.19 | 150.3 | 98.6 | 241.0 | 142.4 | 15.48 | 31.7 |
| angry | 1.09 | 151.9 | 104.2 | 201.6 | 97.5 | 11.43 | 20.5 |
| sad | 1.34 | 113.1 | 83.8 | 134.4 | 50.6 | 8.18 | 12.2 |
| surprised | 1.32 | 178.2 | 97.6 | 309.3 | 211.7 | 19.96 | 42.3 |

![Pitch contours, in real time and time-normalised](../plots/q5_pitch_contours.png)

![F0 range and mean by emotion](../plots/q5_pitch_ranges.png)

**Happy** has a mean F0 of 150.3 Hz, 5.4 semitones above neutral. Its range is 142.4 Hz
against neutral's 23.5 Hz, and its SD is 31.7 Hz against 5.4 Hz. The slope over the final
quarter of the utterance is +313 Hz/s, the steepest of the five.

**Angry** raises the mean by a similar amount, 5.6 semitones, but its range is narrower than
happy's, 97.5 Hz against 142.4 Hz. The two takes are 0.2 semitones apart in mean F0 and
4 semitones apart in range. Angry is also the shortest take, at 1.09 s.

**Sad** has a mean F0 of 113.1 Hz, 0.4 semitones above neutral, and a range of 50.6 Hz
against neutral's 23.5 Hz. Neither figure matches the usual description, in which sadness
lowers mean F0 below neutral and narrows the range. Duration does not separate the two either:
at 1.34 s the sad take is the longest of the four emotional recordings, but the neutral
baseline is longer still at 1.76 s.

The sad recording is therefore not well separated from neutral on any of these measures. One
likely reason is that it was produced on request rather than felt. A performed sad reading
tends to be quieter and slower without lowering the pitch, and the pitch measures here do not
capture the loudness and voice-quality changes that would carry the difference.

**Surprised** has the highest mean F0 at 178.2 Hz, 8.3 semitones above neutral. It also has
the widest range at 211.7 Hz, the highest single value at 309.3 Hz and the largest SD at
42.3 Hz. The contour reaches its maximum about 20% of the way through the utterance and falls
after that.

The happy, angry and surprised takes are 5.4 to 8.3 semitones above neutral in mean F0, and
the sad take is 0.4 semitones above it. Mean F0 therefore separates these four recordings into
two groups, but it does not distinguish the first three from each other, since happy and angry
are only 0.2 semitones apart. Their ranges differ by 4 semitones, so range is the more useful
measure for telling those two apart.

All five recordings end with a rise on "exam". The rise is present in the neutral baseline as
well, so it belongs to the interrogative sentence type rather than to any of the emotions.

\newpage

# Question 6

$s(t) = \sin(2\pi f_1 t)$ for $0 \le t \le \tau$, $\sin(2\pi f_2 t)$ for $\tau < t \le 2$,
and 0 otherwise, with $f_1 = 100$ Hz, $f_2 = 300$ Hz and $\tau = 1$ s. The signal was
synthesised at 8 kHz. Both estimates below use only the STFT magnitudes.

**Settings.** The window is fixed at 20 ms by the question, which is 160 samples at 8 kHz,
Hamming. The hop was set to 1 ms rather than 10 ms, because the hop determines how finely
the transition can be located: a 10 ms hop would restrict the answer to a 10 ms grid. The
FFT bin spacing is $8000/160 = 50$ Hz.

**Estimate 1, peak-frequency track.** Take the largest-magnitude bin in each frame and find
the first frame where it exceeds 200 Hz, the midpoint of the two tones. This gives
$\hat{\tau} = 1.0010$ s, an error of +1.0 ms.

**Estimate 2, band-energy crossover.** Sum the magnitude in a 50 Hz band around each tone and
find where the 300 Hz curve overtakes the 100 Hz curve, interpolating between the straddling
frames. This gives $\hat{\tau} = 1.0001$ s, an error of +0.1 ms. It is more accurate than the
first estimate for two reasons: interpolating between frames removes the 1 ms quantisation,
and summing over a band is less sensitive to which individual bin happens to be largest in a
given frame.

![The signal, its STFT, the peak-frequency track and the band-energy crossover](../plots/q6_tau_estimation.png)

**Precision.** The 0.1 ms figure is more precise than the measurement warrants. Any frame
whose 20 ms span straddles $t = \tau$ contains both tones, so the transition cannot be localised more finely
than the window. Measuring the region where both bands carry significant energy gives 12 ms
rather than the full 20 ms, because the Hamming taper suppresses a tone entering at the edge
of a frame. The result is $\tau = 1.00 \pm 0.01$ s. The window length sets this uncertainty. Shortening
the hop does not reduce it.

![The transition region, showing the smearing caused by the 20 ms window](../plots/q6_transition_zoom.png)

**Resolution trade-off.** A 20 ms window holds exactly 2 cycles of a 100 Hz tone, which is
too few to estimate a frequency sharply: in the spectrogram the 100 Hz component appears as a
smear from roughly 0 to 200 Hz, while the 300 Hz component, with 6 cycles, is better
resolved. A longer window would separate the tones more sharply but smear the transition over
a longer span; a shorter window would locate $\tau$ more tightly but leave the tones barely
distinguishable. For this signal the 20 ms window is a workable compromise, since the tones
are 200 Hz apart, four times the bin spacing.

![The same signal at three window lengths](../plots/q6_window_tradeoff.png)

\newpage

# Question 7: speech emotion recognition

**(a) The application.** Speech emotion recognition (SER) infers a speaker's affective state
from the speech signal, either as discrete labels (anger, happiness, sadness, neutral) or as
continuous dimensions, usually arousal and valence. The dimensional form is often preferred
because discrete labels transfer poorly across languages and cultures. Deployed uses include
call-centre analytics, where rising frustration flags a call for escalation; clinical
screening, where flattened prosody is studied as a marker of depression; driver monitoring;
and conversational agents that adapt when a user is upset. In these systems the words are
already available from speech recognition, and SER is added to recover information that the
transcript does not carry.

**(b) Features used.** *Prosodic*: mean F0, F0 range and variability, contour shape and
slope, intensity, speech rate and pause structure. These carry arousal well; the Q5
measurements above are exactly this kind of input. *Spectral*: MFCCs with their derivatives,
formants, spectral centroid and spectral tilt, the last tracking vocal effort somewhat
independently of pitch. *Voice quality*: jitter, shimmer and harmonics-to-noise ratio, which
describe how the folds vibrate rather than how fast, and separate states that prosody
confuses, such as sadness and tenderness at similar F0. *Learned representations*:
embeddings from wav2vec 2.0, HuBERT or WavLM, which outperform hand-designed sets such as
eGeMAPS but are harder to interpret when they fail.

The two dimensions are not equally easy to recover. Arousal is predicted well from prosody
and energy alone.
Valence is predicted poorly from acoustics, since high-arousal positive and negative states
look similar in F0 and intensity, which is why systems combining audio with the recognised
text gain substantially on valence and little on arousal. The Q5 data shows the same
pattern: happy and angry differ by 0.2 semitones in mean F0.

**(c) Contributions from the levels of description.** *Phonetics*: voice quality and
articulation, with high arousal expanding the vowel space and sadness producing reduced,
centralised articulation. *Phonology*: what matters is not raw F0 but the intonational
contours it realises, including pitch accents and boundary tones, and these are
language-specific. *Morphology*: evaluative affixes carry affect in languages that have them
productively, such as Spanish *-ito*; English has little of this. *Syntax*: sentence type
interacts with prosody, and the Q5 sentence illustrates the risk, since "Did you miss the
exam?" carries a terminal rise in all five recordings simply because it is an interrogative;
a system treating a terminal rise as evidence of surprise would misread every one.
*Semantics*: lexical items carry valence directly, which is the main route by which valence
becomes recoverable. *Pragmatics*: sarcasm is defined by a mismatch between literal content
and intended meaning, so detecting it needs both channels plus context; cultural display
rules also govern how much emotion is expressed at all.

**(d) A limitation.** Systems generalise poorly beyond their training corpus, and the cause
is the data. Emotion cannot be induced on demand reliably or ethically, and there is no
ground truth beyond annotator agreement, so most corpora use acted speech: actors reading
fixed sentences with a target emotion. Acted emotion is exaggerated and prototypical. This makes it
easy to classify, but it differs from spontaneous speech, in which emotions are subtler, often
blended, and frequently suppressed. Accuracy drops substantially when models are tested
cross-corpus. Speaker, language and cultural variation is also large relative to the emotion
effect, and inter-annotator agreement is only moderate, which caps the accuracy any system
can meaningfully claim.

The Q5 recordings show the same problem on a small scale. They were produced deliberately
with the target emotion known in advance, and are almost certainly more distinct from one
another than the same question asked in each of those states would be. The sad recording
differs from neutral by only 0.4 semitones in mean F0, which suggests the delivery was
performed rather than felt.
