# Q5: pitch contour of each emotion recording, extracted with Praat.
# Writes one CSV per file: time, F0 (empty where Praat finds no voicing).
#
# usage: Praat --run q5_pitch.praat <recordings dir> <results dir> <floor> <ceiling>

form Pitch extraction
  sentence indir
  sentence outdir
  positive floor 60
  positive ceiling 500
endform

files$ = "q5_neutral q5_happy q5_angry q5_sad q5_surprised"

writeInfoLine: "file,duration_s,frames,voiced_frames,mean_F0,min_F0,max_F0,sd_F0"

for k from 1 to 5
  name$ = extractWord$ (files$, "")
  files$ = replace$ (files$, name$ + " ", "", 1)

  sound = Read from file: indir$ + "/" + name$ + ".wav"
  dur = Get total duration

  pitch = To Pitch: 0.01, floor, ceiling
  nframes = Get number of frames
  nvoiced = Count voiced frames

  if nvoiced > 0
    meanf = Get mean: 0, 0, "Hertz"
    minf = Get minimum: 0, 0, "Hertz", "Parabolic"
    maxf = Get maximum: 0, 0, "Hertz", "Parabolic"
    sdf = Get standard deviation: 0, 0, "Hertz"
  else
    meanf = undefined
    minf = undefined
    maxf = undefined
    sdf = undefined
  endif

  appendInfoLine: name$, ",", fixed$ (dur, 4), ",", nframes, ",", nvoiced, ",",
    ... fixed$ (meanf, 2), ",", fixed$ (minf, 2), ",", fixed$ (maxf, 2), ",", fixed$ (sdf, 2)

  # per-frame contour
  out$ = outdir$ + "/" + name$ + "_pitch.csv"
  writeFileLine: out$, "time_s,f0_hz"
  for i from 1 to nframes
    t = Get time from frame number: i
    f = Get value in frame: i, "Hertz"
    if f = undefined
      appendFileLine: out$, fixed$ (t, 4), ","
    else
      appendFileLine: out$, fixed$ (t, 4), ",", fixed$ (f, 3)
    endif
  endfor

  removeObject: pitch, sound
endfor
