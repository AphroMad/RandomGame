export function getRole(program, isPercussion) {
    if (isPercussion) return "Drums"
    if (program >= 32 && program <= 39) return "Bass"
    if (program >= 24 && program <= 31) return "Guitar"
    if (program >= 40 && program <= 46) return "Strings"  // 47 excluded
    if (program === 47) return "Percussion"               // Timpani
    if (program >= 48 && program <= 51) return "Ensemble"
    if (program >= 52 && program <= 54) return "Choir"
    if (program === 55) return "Percussion"               // Orchestra Hit
    if (program >= 56 && program <= 71) return "Brass/Wind"
    if (program >= 80 && program <= 95) return "Synth"
    if (program >= 0  && program <= 23) return "Keys/Piano"
    return "Other"
}

export function groupTracksByRole(tracks) {
    const groups = {}

    tracks
        .filter(track => track.notes.length > 0)
        .forEach(track => {
            const role = getRole(track.instrument.number, track.instrument.percussion)
            if (!groups[role]) groups[role] = []
            groups[role].push(track.instrument.name)
        })

    return groups
}