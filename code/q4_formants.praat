# Q4: formant tracks for "beat" and "bit", Burg method.
#
# usage: Praat --run q4_formants.praat <recordings dir> <results dir> <max formant Hz>

form Formants
  sentence indir
  sentence outdir
  positive maxformant 5500
endform

files$ = "q4_beat q4_bit"

writeInfoLine: "file,duration_s,frames"

for k from 1 to 2
  name$ = extractWord$ (files$, "")
  files$ = replace$ (files$, name$ + " ", "", 1)

  sound = Read from file: indir$ + "/" + name$ + ".wav"
  dur = Get total duration

  # intensity is used later to find the vowel; save it alongside
  intensity = To Intensity: 100, 0, "yes"
  selectObject: sound
  formant = To Formant (burg): 0.0, 5.0, maxformant, 0.025, 50
  nframes = Get number of frames

  appendInfoLine: name$, ",", fixed$ (dur, 4), ",", nframes

  out$ = outdir$ + "/" + name$ + "_formants.csv"
  writeFileLine: out$, "time_s,f1_hz,f2_hz,f3_hz,intensity_db"
  for i from 1 to nframes
    selectObject: formant
    t = Get time from frame number: i
    f1 = Get value at time: 1, t, "hertz", "Linear"
    f2 = Get value at time: 2, t, "hertz", "Linear"
    f3 = Get value at time: 3, t, "hertz", "Linear"
    selectObject: intensity
    db = Get value at time: t, "Cubic"
    f1$ = ""
    f2$ = ""
    f3$ = ""
    db$ = ""
    if f1 <> undefined
      f1$ = fixed$ (f1, 2)
    endif
    if f2 <> undefined
      f2$ = fixed$ (f2, 2)
    endif
    if f3 <> undefined
      f3$ = fixed$ (f3, 2)
    endif
    if db <> undefined
      db$ = fixed$ (db, 2)
    endif
    appendFileLine: out$, fixed$ (t, 4), ",", f1$, ",", f2$, ",", f3$, ",", db$
  endfor

  removeObject: formant, intensity, sound
endfor
