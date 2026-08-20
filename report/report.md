---
title: "Speech Analysis and Linguistics, Assignment 1"
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
pulses shown. Stops begin at the onset of closure and the following vowel at the first
glottal pulse, and fricatives at the onset of frication.

**Mains interference.** All the recordings contain a steady 100 Hz tone, the second harmonic
of the 50 Hz mains supply. It is present during the silences as well as during speech, and it
sits close to the speaker's own pitch, so Praat mistakes it for voicing. On the raw whispered
file Praat reports 18.8% voiced frames, but those frames are spread evenly across the whole
file instead of being concentrated in the speech, which is what identifies them as
interference rather than phonation.

A high-pass filter at 150 Hz removes the tone. Pitch tracking still works on the filtered
signal, because it measures how often the waveform repeats and the filter does not change
that. Pitch and formants were therefore measured on the filtered recordings, and energy and
ZCR on the originals, since filtering would change the quantity Q1 asks for.

Everything regenerates with `code/run_all.sh`.

\newpage

# Question 1

## (a) Segmentation

The sentence recorded was "The big pig sat on a thick sheet.", transcribed as
ð ə **|** b ɪ ɡ **|** p ɪ ɡ **|** s æ t **|** ɒ n **|** ə **|** θ ɪ k **|** ʃ iː t, 20 phonemes. Boundaries were
marked in Praat on a wideband spectrogram as described in the Method. The delivery was
slow enough to leave audible pauses between some words; these are labelled as silence
rather than absorbed into the neighbouring stop closure, which would otherwise drag that
consonant's mean energy down. The TextGrid is `textgrids/q1_normal.TextGrid`.

## (b) Short-time energy and zero-crossing rate

Both were computed with a 20 ms Hamming window and a 10 ms shift, giving 552 frames for
the 5.53 s recording. Energy is the sum of squared windowed samples in each frame. ZCR is
the proportion of adjacent sample pairs that change sign, computed on the unwindowed frame:
tapering the frame towards zero at its edges introduces sign changes that belong to the
window rather than to the signal.

![Waveform, short-time energy and ZCR with the phoneme boundaries marked](../plots/q1b_energy_zcr.png)

The two measures behave in opposite directions. Energy peaks on the vowels and drops by two
to three orders of magnitude during stop closures. ZCR is near zero through the voiced
portions and rises sharply at exactly four places: /s/ at 2.9 s, /θ/ at 3.7 s, /ʃ/ at 4.0 s
and the final /t/ release at 4.4 s.

## (c) Averages within each phoneme

| phone | class | voicing | duration (ms) | mean energy | mean ZCR |
|---|---|---|---|---|---|
| ð | non-vowel | voiced | 39.9 | 1.93e-02 | 0.0323 |
| ə | vowel | voiced | 304.3 | 5.62e-01 | 0.0072 |
| b | non-vowel | voiced | 20.0 | 1.87e-01 | 0.0057 |
| ɪ | vowel | voiced | 229.5 | 1.05e+00 | 0.0165 |
| ɡ | non-vowel | voiced | 84.8 | 2.81e-02 | 0.0230 |
| p | non-vowel | unvoiced | 114.7 | 7.43e-03 | 0.0084 |
| ɪ | vowel | voiced | 259.4 | 6.59e-01 | 0.0127 |
| ɡ | non-vowel | voiced | 84.8 | 6.08e-02 | 0.0126 |
| s | non-vowel | unvoiced | 139.7 | 2.21e-02 | 0.1719 |
| æ | vowel | voiced | 174.6 | 9.77e-01 | 0.0264 |
| t | non-vowel | unvoiced | 89.8 | 2.73e-02 | 0.0143 |
| ɒ | vowel | voiced | 69.8 | 3.99e-01 | 0.0125 |
| n | non-vowel | voiced | 54.9 | 8.31e-01 | 0.0057 |
| ə | vowel | voiced | 84.8 | 6.67e-01 | 0.0043 |
| θ | non-vowel | unvoiced | 44.9 | 5.29e-02 | 0.0369 |
| ɪ | vowel | voiced | 94.8 | 8.18e-01 | 0.0190 |
| k | non-vowel | unvoiced | 119.7 | 9.16e-03 | 0.0153 |
| ʃ | non-vowel | unvoiced | 199.5 | 7.02e-02 | 0.1589 |
| iː | vowel | voiced | 159.6 | 4.58e-01 | 0.0080 |
| t | non-vowel | unvoiced | 194.6 | 1.68e-02 | 0.0336 |

Grouped:

| grouping | n | mean energy | mean ZCR |
|---|---|---|---|
| vowel | 8 | 6.98e-01 | 0.0133 |
| non-vowel | 12 | 1.11e-01 | 0.0432 |
| voiced | 13 | 5.16e-01 | 0.0143 |
| unvoiced | 7 | 2.94e-02 | 0.0627 |

![Per-phoneme averages grouped by class. Bars are group means with SD, dots are individual phonemes.](../plots/q1_class_comparison.png)

**Vowels against non-vowels.** Vowels average 6.3 times the energy of non-vowels and about
one third of the ZCR. The energy difference follows from the source. Vowels are produced with an open vocal
tract and a vibrating larynx, so they carry almost all of the acoustic energy of the
utterance. The ZCR difference follows from where that energy sits
in frequency. A periodic signal whose energy is concentrated in low formants crosses zero
few times per frame, while the aperiodic high-frequency noise of a fricative crosses many
times.

**Voiced against unvoiced.** The separation is larger. Voiced segments average 17.6 times
the energy of unvoiced ones, and unvoiced segments have 4.4 times the ZCR. Voicing is the
better predictor of both measures than the vowel distinction, which makes sense because the
vowel class is a subset of the voiced class, and the voiced consonants /n/, /b/ and /ð/
carry the vowel-like pattern with them.

**Individual phonemes that do not follow the pattern.** /n/ has an energy of 8.31e-01,
higher than four of the eight vowels, and the lowest ZCR of any segment at 0.0057. It is
a voiced non-vowel, so it raises the non-vowel average and lowers the non-vowel ZCR average.
Grouping by voicing rather than by vowel class puts it on the correct side. /b/ likewise
has a relatively high energy of 1.87e-01 for a stop, because it is only 20 ms long and sits
between two vowels, so the frames covering it are dominated by the surrounding voicing.
Among the unvoiced segments, /p/ and /k/ have the lowest energies of all, 7.43e-03 and
9.16e-03, since both intervals are mostly closure silence.

The clearest single result is the ZCR of /s/ (0.1719) and /ʃ/ (0.1589), which are five to
ten times any voiced segment. Interestingly /θ/ reaches only 0.0369, well below the other
two fricatives, because it is much weaker and its frames are partly filled by the low-level
background rather than by frication.

\newpage

# Question 2

The same sentence was recorded whispered and segmented the same way
(`textgrids/q2_whisper.TextGrid`). The two recordings are compared below.

| measure | normal | whisper |
|---|---|---|
| speech duration | 3.238 s | 3.203 s |
| voiced frames | 132 / 549 (24.0%) | 2 / 580 (0.3%) |
| mean F0 | 101.9 Hz | not measurable |
| RMS | −30.2 dB | −41.6 dB |
| spectral centroid | 633 Hz | 829 Hz |
| energy below 1 kHz vs above | +9.5 dB | −5.0 dB |
| vowel / non-vowel energy ratio | 6.3 | 1.6 |
| voiced / unvoiced energy ratio | 17.6 | 1.0 |

![The same sentence, normal above and whispered below](../plots/q2_spectrograms.png)

## (a) What is unchanged, and is the message preserved?

The message is preserved. The whispered recording is intelligible and every phoneme in the
sentence can still be located and labelled, which is why the same 20-phoneme segmentation
applies to both files.

What survives is everything produced above the larynx. The vocal tract still takes the same
sequence of shapes, so place and manner of articulation are unchanged and the formant
pattern remains. The spectrograms show the same formant bands in both recordings, produced
by noise in the whisper instead of by glottal pulses. Total speech duration is almost identical,
3.238 s against 3.203 s, so the timing of the utterance is preserved as well. Fricatives are
the least affected of all, since /s/, /ʃ/ and /θ/ were already produced with turbulent noise
and no voicing.

## (b) What does whisper gain to become normal speech, and is speaker identity preserved?

The addition is phonation. Voicing takes the whisper's aperiodic noise source and replaces it
with a periodic one. That brings a fundamental frequency and a harmonic spectrum, and with
them intonation, stress, and the pitch contour that separates a statement from a question. Measured here, that
is the difference between 24.0% voiced frames at a mean F0 of 101.9 Hz and 0.3% voiced
frames with no measurable F0.

The energy consequences are large. The whisper is 11.4 dB quieter overall, and its spectral
balance is shifted 14.5 dB towards high frequencies. Within the whisper the voiced/unvoiced
energy ratio collapses from 17.6 to 1.0, meaning the phonemes that were separated by 25 dB of
energy in normal speech are indistinguishable on that measure once phonation is removed.

Speaker identity is only partly preserved. The vocal tract is unchanged, so the cues that
depend on its size and shape survive, meaning formant frequencies and formant spacing,
together with learned habits of timing and articulation. What is lost is everything
carried by the glottal source, which includes mean pitch, pitch range, and the detail of the
voice quality such as breathiness and creak. This is why whispered speech is recognisable as
a person but much harder to identify confidently, and why speaker verification systems
degrade sharply on whispered input.

## (c) The state of the vocal folds

In whispering the vocal folds are brought close together (adducted) but not close enough, and
not under the right tension, to be set into self-sustaining vibration. Typically the front
part of the glottis is closed while a triangular opening remains at the back, at the
cartilaginous portion, called the glottal chink. Air forced through this narrow opening
becomes turbulent, and that turbulence is the sound source. It is aperiodic, which is why
the whisper has no F0 to measure.

Other states of the vocal folds:

- **Open (abduction)**, as in quiet breathing and in voiceless sounds such as /s/ and /p/,
  where the folds are apart and air passes without obstruction.
- **Modal voice**, the normal speaking state, where the folds are adducted and vibrate
  periodically. This produced the 101.9 Hz measured in the normal recording.
- **Breathy voice**, where the folds vibrate but remain slightly apart, so periodic voicing
  and turbulent noise are present together.
- **Creaky voice** (vocal fry), with the folds tightly adducted and slack, giving very low
  and irregular pulses.
- **Full closure**, as in the glottal stop, where the folds are pressed together and airflow
  stops completely.

## (d) Can every English word be distinguished in a whisper? "pig" against "big"

Not equally well. Any contrast that depends on voicing loses its primary cue, because
voicing is precisely what whispering removes. English has many such minimal pairs:
pig/big, tie/die, coat/goat, fan/van, sue/zoo, and word-finally tap/tab and seat/seed.

For "pig" against "big" the primary distinction is the presence of vocal fold vibration
during and immediately after the closure. In the whisper that cue is gone from both, so a
listener has to rely on secondary cues, which survive but are weaker:

- **Voice onset time.** In the recordings here, the release-to-vowel interval is 16 ms for
  /b/ against 20 ms for /p/ in normal speech, but 8 ms against 92 ms in the whisper. The
  difference is larger in the whisper, not smaller, which suggests the aspiration of /p/ is
  exaggerated when voicing is unavailable to carry the contrast.
- **Burst strength.** The release of a voiceless stop is typically more forceful.
- **Preceding vowel duration**, which is the main cue for final voicing contrasts such as
  tap/tab, and is unaffected by whispering.

So the contrast degrades rather than disappearing outright. This is consistent with the
spectrograms, where the two segments look alike in the low frequencies, which is where
voicing would show, and differ in the timing and intensity of the release.

## (e) How can a mimic imitate another speaker's voice?

A voice is a mixture of properties that can be learned and properties fixed by anatomy, and
a mimic can only copy the first group.

The learnable layer is large. It includes mean pitch and pitch range, intonation patterns,
speech rate and rhythm, voice quality such as breathiness or creak, and the habits of
pronunciation and word choice that make a person recognisable. Trained imitators also adjust vocal tract shape deliberately, for
example by rounding the lips or lowering the larynx, which shifts the formants towards the
target speaker's.

What cannot be changed is the physical apparatus, meaning vocal tract length, the resonant
cavities of the nose and sinuses, and the size and mass of the vocal folds. These set the
formant frequencies and the fine detail of the glottal source. A good impression therefore
works by reproducing the salient, learnable cues that listeners actually attend to, mainly
prosody and a few distinctive articulations, while the underlying acoustics remain those of
the imitator. This is why impressions convince human listeners far more easily than they
fool a speaker verification system, which measures exactly the spectral detail the mimic
cannot alter.

\newpage

# Question 3

**(a) "reusable" = "re-" + "use" + "-able".** This is **morphology**, which deals with the
internal structure of words and how their parts combine. Two derivational affixes attach to a free root, and the order is
[[re + use] + able].

**(b) "bank" as riverside or financial institution.** This is **semantics**, which deals with
the relation between a form and its meanings. This is homonymy rather than polysemy, as the river sense comes through
Old Norse and the financial sense through Italian *banca*, so they are two distinct lexical
items sharing a form.

**(c) "The teacher explained the lesson to the students" is SVO.** This is **syntax**, which
deals with the arrangement of constituents and the word order English uses. It does not depend on what the words mean.

**(d) "fan" and "van" differ by one phoneme.** This is **phonology**. The minimal-pair test
establishes that /f/ and /v/ are contrastive phonemes of English. Phonetics would describe how they
differ physically (both labiodental fricatives, /v/ voiced); phonology concerns the fact
that the difference distinguishes words. The same phonetic difference is not contrastive in
every language.

**(e) "It's getting dark in here" as a request.** This is **pragmatics**. The literal content
is a statement, while the intended force is a request. This is an indirect speech act, resolved by
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
the transition can be located, and a 10 ms hop would restrict the answer to a 10 ms grid. The
FFT bin spacing is $8000/160 = 50$ Hz.

**Estimate 1, peak-frequency track.** Take the largest-magnitude bin in each frame and find
the first frame where it exceeds 200 Hz, the midpoint of the two tones. This gives
$\hat{\tau} = 1.0010$ s, an error of +1.0 ms.

**Estimate 2, band-energy crossover.** Sum the magnitude in a 50 Hz band around each tone and
find where the 300 Hz curve overtakes the 100 Hz curve, interpolating between the straddling
frames. This gives $\hat{\tau} = 1.0001$ s, an error of +0.1 ms. It is more accurate than the
first estimate for two reasons. Interpolating between frames removes the 1 ms quantisation,
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
too few to estimate a frequency sharply. In the spectrogram the 100 Hz component appears as
a smear from roughly 0 to 200 Hz, while the 300 Hz component, with 6 cycles, is better
resolved. A longer window would separate the tones more sharply but smear the transition over
a longer span; a shorter window would locate $\tau$ more tightly but leave the tones barely
distinguishable. For this signal the 20 ms window is a workable compromise, since the tones
are 200 Hz apart, four times the bin spacing.

![The same signal at three window lengths](../plots/q6_window_tradeoff.png)

\newpage

# Question 7

The application chosen is **speech emotion recognition**.

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
confuses, such as sadness and tenderness at similar F0. *Learned features*: rather
than measuring these quantities by hand, recent systems let a neural network learn its own
representation from large amounts of unlabelled speech, using models such as wav2vec 2.0 or
HuBERT. These perform better on most benchmarks but are harder to interpret when they fail.

The two dimensions are not equally easy to recover. Arousal is predicted well from prosody
and energy alone.
Valence is predicted poorly from acoustics, since high-arousal positive and negative states
look similar in F0 and intensity, which is why systems combining audio with the recognised
text gain substantially on valence and little on arousal. The Q5 data shows the same
thing, with happy and angry differing by only 0.2 semitones in mean F0.

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
ground truth beyond annotator agreement, so most corpora use acted speech, with actors
reading fixed sentences in a target emotion. Acted emotion is exaggerated and prototypical. This makes it
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
