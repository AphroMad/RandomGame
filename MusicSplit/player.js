import 'https://cdn.jsdelivr.net/npm/tone@14.7.77/build/Tone.js'
const Tone = window.Tone

let activeGroup = null
let startTime = 0
let endTime = 0
let timerInterval = null
let _onTick = null
let _onStop = null
let started = false

export function getActiveGroup() { return activeGroup }

export function formatTime(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0')
    const s = Math.floor(seconds % 60).toString().padStart(2, '0')
    return `${m}:${s}`
}

export function stopAll(onStop) {
    clearInterval(timerInterval)
    timerInterval = null
    try { Tone.Transport.stop() } catch(e) {}
    if (onStop) onStop()
}

function resetTransport() {
    try {
        Tone.Transport.stop()
        Tone.Transport.position = 0
        // Remove all scheduled events by cancelling from the start
        Tone.Transport.cancel(0)
    } catch(e) {}
}

export async function playGroup(tracks, groupName, onTick, onStop) {
    // Unlock audio context — must happen first, in user gesture
    if (!started) {
        await Tone.start()
        started = true
    }

    stopAll()
    resetTransport()

    _onTick = onTick
    _onStop = onStop
    activeGroup = groupName

    const allNotes = tracks.flatMap(t => t.notes)
    if (!allNotes.length) return

    startTime = Math.min(...allNotes.map(n => n.time))
    endTime = Math.max(...allNotes.map(n => n.time + n.duration))
    const duration = endTime - startTime

    for (const track of tracks) {
        if (!track.notes.length) continue

        let synth
        if (track.instrument.percussion) {
            synth = new Tone.MembraneSynth({ pitchDecay: 0.05, octaves: 4 }).toDestination()
        } else if (groupName === 'Bass') {
            synth = new Tone.Synth({ oscillator: { type: 'triangle' }, envelope: { attack: 0.02, decay: 0.1, sustain: 0.8, release: 0.5 } }).toDestination()
        } else if (groupName === 'Brass/Wind') {
            synth = new Tone.Synth({ oscillator: { type: 'sawtooth' }, envelope: { attack: 0.05, decay: 0.1, sustain: 0.7, release: 0.3 } }).toDestination()
        } else if (groupName === 'Strings' || groupName === 'Ensemble') {
            synth = new Tone.Synth({ oscillator: { type: 'sine' }, envelope: { attack: 0.3, decay: 0.1, sustain: 0.9, release: 1 } }).toDestination()
        } else {
            synth = new Tone.Synth({ oscillator: { type: 'triangle' }, envelope: { attack: 0.02, decay: 0.1, sustain: 0.5, release: 0.5 } }).toDestination()
        }

        const part = new Tone.Part((time, note) => {
            synth.triggerAttackRelease(note.freq, note.duration, time, note.velocity)
        }, track.notes.map(n => ({
            time: n.time - startTime,
            freq: Tone.Frequency(n.midi, 'midi').toFrequency(),
            duration: n.duration,
            velocity: n.velocity
        })))

        part.start(0)
    }

    Tone.Transport.scheduleOnce(() => stopAll(onStop), duration)
    Tone.Transport.start()

    timerInterval = setInterval(() => {
        const elapsed = Tone.Transport.seconds
        if (onTick) onTick(elapsed, duration)
    }, 100)
}

export async function seekTo(fraction) {
    if (!endTime) return
    const duration = endTime - startTime
    const seekSeconds = Math.max(0, Math.min(1, fraction)) * duration

    clearInterval(timerInterval)
    resetTransport()
    Tone.Transport.seconds = seekSeconds
    Tone.Transport.start()

    timerInterval = setInterval(() => {
        const elapsed = Tone.Transport.seconds
        if (_onTick) _onTick(elapsed, duration)
        if (elapsed >= duration) stopAll(_onStop)
    }, 100)
}
