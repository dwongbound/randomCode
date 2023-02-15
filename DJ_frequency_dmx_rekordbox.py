import librosa
import numpy as np
import pyenttec as dmx
import mido
import rekordbox

# Set up Rekordbox API client
client = rekordbox.Client()
client.connect()

# Set up DMX client
with dmx.DMXConnection('COM1') as dmx_client:  # Replace with your DMX interface port

    # Define DMX channel ranges for each frequency group
    bass_channels = range(1, 4)
    mid_channels = range(4, 7)
    treble_channels = range(7, 10)

    # Set up MIDI client to listen for trigger messages
    midi_client = mido.open_input('MIDI Controller')  # Replace with the name of your MIDI input device

    # Start the loop to listen for trigger messages and analyze the frequency spectrum
    while True:
        # Get information about the currently playing track
        track = client.get_current_track()

        # Load the audio file and analyze the frequency spectrum
        y, sr = librosa.load(track.location)
        fft = np.abs(librosa.stft(y))

        # Divide the frequency spectrum into three bands
        freq_bands = librosa.fft_frequencies(sr=sr)
        bass_mask = (freq_bands >= 20) & (freq_bands < 250)
        mid_mask = (freq_bands >= 250) & (freq_bands < 2000)
        treble_mask = (freq_bands >= 2000) & (freq_bands <= 20000)
        bass_energy = np.sum(fft[bass_mask])
        mid_energy = np.sum(fft[mid_mask])
        treble_energy = np.sum(fft[treble_mask])

        # Calculate the brightness level for each channel based on the energy level of its frequency band
        bass_brightness = int(min(bass_energy / 10000, 1.0) * 255)
        mid_brightness = int(min(mid_energy / 10000, 1.0) * 255)
        treble_brightness = int(min(treble_energy / 10000, 1.0) * 255)

        # Set the brightness levels for each channel
        dmx_client.set_channel_levels(bass_channels, [bass_brightness] * len(bass_channels))
        dmx_client.set_channel_levels(mid_channels, [mid_brightness] * len(mid_channels))
        dmx_client.set_channel_levels(treble_channels, [treble_brightness] * len(treble_channels))

        # Wait for the next trigger message
        for message in midi_client.iter_pending():
            # Handle the MIDI message here (e.g. toggle the lights on/off)
            pass