# Magic Push-to-Talk

Magic Push-to-Talk (MagicPTT) is a desktop application designed to provide a customizable and intelligent push-to-talk functionality. The application listens to your microphone input and automatically activates a push-to-talk key when your voice crosses a certain threshold. The app also allows you to configure various settings, including the microphone input, threshold levels, push-to-talk key, and more.

## Features

- **Automatic Noise Threshold Detection:** Automatically calibrates the noise floor and adjusts the threshold dynamically.
- **Manual Threshold Mode:** Allows you to set a manual threshold for activation.
- **Customizable Push-to-Talk Key:** Set any key as your push-to-talk trigger.
- **Test Mode:** Test the functionality without triggering actual key presses.
- **Configurable Release Delay:** Set a custom delay before deactivating the push-to-talk key.
- **Visual Audio Meter:** Displays real-time audio levels and threshold indication.
- **Persistent Configuration:** Save and load settings from a configuration file.

## Requirements

- Python 3.6+
- PyQt6
- PyAudio
- pynput
- numpy
- pywin32 (for Windows key event handling)

## Installation

1. Clone the repository or download the source code.
2. Install the required Python packages:
    ```sh
    pip install PyQt6 pyaudio pynput numpy pywin32
    ```
3. Run the application:
    ```sh
    python magic_ptt.py
    ```

## Usage

1. **Microphone Selection:** Choose your preferred microphone from the dropdown list.
2. **Push-to-Talk Key:** Click the button to set a custom push-to-talk key. The default key is 'V'.
3. **Threshold Offset:** Adjust the threshold offset to fine-tune the sensitivity.
4. **Release Delay:** Set the release delay duration for how long the push-to-talk key remains active after speaking.
5. **Manual Threshold Mode:** Enable manual threshold mode and set the threshold level using the slider.
6. **Start Monitoring:** Click the "Start" button to begin monitoring your audio input.
7. **Test Mode:** Enable test mode if you want to test the application without sending actual key presses.
8. **Configuration:** Settings are automatically saved on exit and loaded on startup.

## Important Note

For the application to function correctly in certain games, such as Valorant, **you must run Magic Push-to-Talk as an administrator**. This is necessary for the app to interact with the game's input system, which may have elevated security restrictions.

## Customization

- **Threshold Offset:** Adjust the slider to change the dB level required to activate the push-to-talk key.
- **Manual Threshold:** Set a specific dB level for the manual mode.
- **Release Delay:** Control how long the key stays active after your voice drops below the threshold.

## Troubleshooting

- **Microphone Not Detected:** Ensure your microphone is correctly connected and recognized by the system.
- **Key Presses Not Working:** Verify that the correct push-to-talk key is set. Check the test mode setting if you're not seeing key presses.
- **High Latency or Delays:** Adjust the release delay setting or the update interval for smoother performance.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements or fixes.

## Acknowledgments

- [PyQt6](https://pypi.org/project/PyQt6/) for the GUI framework.
- [PyAudio](https://pypi.org/project/PyAudio/) for handling audio streams.
- [pynput](https://pypi.org/project/pynput/) for managing keyboard input.
- [pywin32](https://pypi.org/project/pywin32/) for Windows-specific key handling.

