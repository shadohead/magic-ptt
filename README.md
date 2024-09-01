# Magic Push-to-Talk (MagicPTT)

Magic Push-to-Talk (MagicPTT) is a desktop app that provides customizable push-to-talk functionality by activating a key when your voice crosses a set threshold.

## 📥 Download

You can **download the latest version as a `.exe` file** from the [Releases](../../releases) tab for easy installation.

---

## ✨ Features

- **Automatic & Manual Thresholds:** Dynamic calibration or manual setting.
- **Custom Push-to-Talk Key:** Assign any key as your trigger.
- **Test Mode:** Test without sending key presses.
- **Release Delay:** Customize how long the key stays active.
- **Audio Meter:** Real-time audio levels display.
- **Configurable:** Save/load settings automatically.

## 🛠 Requirements

- Python 3.6+
- PyQt6, PyAudio, pynput, numpy, pywin32

## 🚀 Installation

1. Clone or download the source code.
2. Install dependencies:
    ```sh
    pip install PyQt6 pyaudio pynput numpy pywin32
    ```
3. Run the app:
    ```sh
    python magic_ptt.py
    ```

> **Note:** You can also download the latest `.exe` file from the [Releases](../../releases) tab for easy installation.

## 📝 Usage

1. **Select Microphone:** Choose your mic.
2. **Set Push-to-Talk Key:** Default is 'V'.
3. **Adjust Threshold & Delay:** Fine-tune sensitivity and delay.
4. **Enable Test Mode:** Test without actual key presses.
5. **Start Monitoring:** Begin audio monitoring.

> **Note:** Run as administrator for certain games like Valorant.

## 💖 Support the Project

If you find Magic Push-to-Talk useful, consider supporting its development:

- [PayPal](https://www.paypal.me/shadohead)

## 📄 License

Licensed under GPL 3.0. See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Fork, improve, and submit a pull request.

## 🙏 Acknowledgments

- [PyQt6](https://pypi.org/project/PyQt6/)
- [PyAudio](https://pypi.org/project/PyAudio/)
- [pynput](https://pypi.org/project/pynput/)
- [pywin32](https://pypi.org/project/pywin32/)
