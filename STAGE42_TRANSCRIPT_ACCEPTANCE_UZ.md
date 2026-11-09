# Stage 42 — Samsung A14 / Android Transcript Acceptance Checklist

**Status at release:** NOT TESTED ON PHYSICAL DEVICE.  
**Device target:** Samsung Galaxy A14, current Chrome and Samsung Internet available on device.  
**Test URL:** use the repository URL currently shown in `DEPLOY_TARGET.txt`; confirm repository name before deploying.

## Before testing

- [ ] Make a JSON progress backup from Settings.
- [ ] Open the site in the full Chrome browser, not an in-app webview.
- [ ] Confirm the page is HTTPS and fully loaded.
- [ ] Chrome → Site settings → Microphone → Allow.
- [ ] Connect to a stable internet connection for the browser ASR test.
- [ ] Keep the screen awake during the test.

## Live ASR tests

### Part 1
- [ ] Open Speaking → Part 1.
- [ ] Select English (UK), tap **Start live transcript**, allow microphone access if prompted.
- [ ] Speak a 10–15 second answer in English.
- [ ] Confirm interim words may appear while speaking.
- [ ] Confirm final text remains in the Part 1 raw transcript field after recognition ends.
- [ ] Tap Stop and confirm the final text remains.
- [ ] Navigate away and return; confirm text is still present.

### Part 2 and Part 3
- [ ] Repeat the live test for Part 2.
- [ ] Repeat the live test for Part 3.
- [ ] Start one Part, then start another; confirm only the newer session remains active and the old segment's committed text is preserved.
- [ ] Change recognition language while listening; confirm session stops and asks for a fresh Start.

### Recovery / fallback
- [ ] Deny microphone permission; confirm an understandable permission message appears.
- [ ] Re-enable permission and retry.
- [ ] Disable internet; confirm a network/offline warning appears and previously saved transcript remains. Browser ASR may not work offline.
- [ ] If live ASR is unsupported or unavailable, tap **Manual / keyboard dictation**.
- [ ] Type a sentence manually and confirm it remains after navigating away and returning.
- [ ] Use the Samsung Keyboard or Gboard microphone with English selected; confirm dictation enters the same raw transcript field.
- [ ] While live ASR is active, edit the raw transcript manually; confirm recognition stops and late events do not overwrite the manual text.
- [ ] Clear Part 3; confirm Part 1 and Part 2 text remain untouched.

### Audio recording remains separate
- [ ] Record a Part 1 audio clip using its dedicated Part audio recorder.
- [ ] Stop and save; confirm playback works.
- [ ] Reload the page; confirm the audio clip still appears and plays.
- [ ] Repeat for Part 2 and Part 3 if needed.
- [ ] Confirm transcript and audio can both be retained for the same Part.

## Result recording

| Test | Result | Notes / browser version |
|---|---|---|
| Chrome Part 1 live transcript | NOT TESTED | |
| Chrome Part 2 live transcript | NOT TESTED | |
| Chrome Part 3 live transcript | NOT TESTED | |
| Stop + persistence after reload | NOT TESTED | |
| Permission denied recovery | NOT TESTED | |
| Offline/network warning | NOT TESTED | |
| Manual typing autosave | NOT TESTED | |
| Samsung/Gboard voice typing | NOT TESTED | |
| Manual edit protects against late ASR result | NOT TESTED | |
| Segment-specific clear | NOT TESTED | |
| Part audio saved and restored | NOT TESTED | |
| Samsung Internet compatibility | NOT TESTED | |

**Acceptance rule:** do not mark the physical device as PASS until the test has actually been performed. A mock browser test or static code check is not proof that Android's speech service is available.
