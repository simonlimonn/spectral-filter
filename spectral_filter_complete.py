import numpy as np
import sounddevice as sd
import time

# ======================================================
# USER PARAMETERS
# ======================================================

SAMPLE_RATE = 48000
BLOCK_SIZE  = 1024          # buffer size
FFT_SIZE    = 1024            # keep same as block size for clarity

LOW_CUT     = 2000.0            # Hz
HIGH_CUT    = 4000.0          # Hz

GAIN        = 1.0

# ======================================================
# AUDIO DEVICE SELECTION
# ======================================================

def choose_device():
    devices = sd.query_devices()

    print("\nAvailable audio devices:")
    for i, d in enumerate(devices):
        print(f"[{i}] {d['name']} | in:{d['max_input_channels']} out:{d['max_output_channels']}")

    in_dev = int(input("\nInput device index: "))
    out_dev = int(input("Output device index: "))

    in_ch = int(input("Input channels (1 or 2 recommended): "))
    out_ch = int(input("Output channels (1 or 2 recommended): "))

    return in_dev, out_dev, in_ch, out_ch

# ======================================================
# AUDIO CALLBACK (THE WHOLE DSP HAPPENS HERE)
# ======================================================

def audio_callback(indata, outdata, frames, time_info, status):
    """
    This function is called repeatedly by the audio engine.
    Each call processes one block of audio.
    """

    # --------------------------------------------------
    # 1. MIX INPUT TO MONO
    # --------------------------------------------------
    # indata shape: (frames, channels)
    x = np.zeros(frames)

    for i in range(frames):
        s = 0.0
        for ch in range(indata.shape[1]):
            s += indata[i, ch]
        x[i] = s / indata.shape[1]

    # --------------------------------------------------
    # 2. FFT (time domain -> frequency domain)
    # --------------------------------------------------
    X = np.fft.rfft(x)

    # --------------------------------------------------
    # 3. HARD BAND FILTER
    # --------------------------------------------------
    X_filtered = np.zeros_like(X)

    # Frequency resolution per bin
    bin_width = SAMPLE_RATE / FFT_SIZE

    # Loop over FFT bins
    for f in range(len(X)):
        # Frequency represented by bin k
        freq = f * bin_width
  
        ########################
        # START YOUR CODE HERE #
        ########################
        if freq > LOW_CUT and freq < HIGH_CUT:
            X_filtered[f] = X[f]

        # Decide whether this frequency survives

        ########################
        # END YOUR CODE HERE #
        ########################
        

    # --------------------------------------------------
    # 4. INVERSE FFT (frequency -> time)
    # --------------------------------------------------
    y = np.fft.irfft(X_filtered)

    # --------------------------------------------------
    # 5. APPLY GAIN
    # --------------------------------------------------
    for i in range(len(y)):
        y[i] *= GAIN

    # --------------------------------------------------
    # 6. WRITE TO OUTPUT
    # --------------------------------------------------
    if outdata.shape[1] == 1:
        # mono output
        for i in range(frames):
            outdata[i, 0] = y[i]
    else:
        # stereo output (duplicate mono)
        for i in range(frames):
            outdata[i, 0] = y[i]
            outdata[i, 1] = y[i]

# ======================================================
# MAIN
# ======================================================

def main():
    print("\nExplicit FFT Band Filter")
    print(f"FFT size: {FFT_SIZE}")
    print(f"Sample rate: {SAMPLE_RATE} Hz")
    print(f"Pass band: {LOW_CUT} – {HIGH_CUT} Hz\n")

    in_dev, out_dev, in_ch, out_ch = choose_device()

    with sd.Stream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        device=(in_dev, out_dev),
        channels=(in_ch, out_ch),
        dtype="float32",
        callback=audio_callback,
    ):
        print("\nRunning... Ctrl+C to stop.")
        while True:
            time.sleep(0.5)

# ======================================================
# Entry point 
# ======================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")