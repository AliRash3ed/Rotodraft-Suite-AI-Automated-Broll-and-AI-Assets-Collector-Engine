# Contributing to RotoDraft Suite 🎬

Thank you for your interest in contributing to **RotoDraft Suite — Automatic Script-to-B-Roll & Asset Collector Engine**! 

We welcome contributions from developers, creators, video editors, and AI engineers across the globe. This project was built to eliminate expensive SaaS subscriptions ($40-$60/month) and make AI video creation accessible to everyone.

---

## 🛠️ How You Can Contribute

1. **Add New Stock Media Vaults**: Integrate APIs or scrapers for platforms like Unsplash, Freepik, Archive.org, Pond5, etc.
2. **Add New AI Providers / Adapters**: Connect new local LLMs (Ollama, LM Studio, vLLM, Exo) or cloud APIs (Mistral, Cohere, xAI Grok).
3. **NLE Exporters**: Enhance support for Final Cut Pro XML, Avid AAF, Blender VSE, or DaVinci Fusion scripts.
4. **UI / UX Improvements**: Improve responsive layouts, keybindings, sound effects, or themes.
5. **Bug Reports & Fixes**: Report issues with FFmpeg flags, Windows/Linux path handling, or API rate limiters.

---

## 🚀 Development Setup

1. **Fork & Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rotodraft-suite.git
   cd rotodraft-suite
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Test Suite**:
   ```bash
   python tests/test_suite.py
   ```

5. **Start the Web Studio**:
   ```bash
   python app.py
   ```
   Open `http://localhost:8001` in your browser.

---

## 📋 Pull Request Guidelines

- Ensure all existing tests pass: `python tests/test_suite.py`.
- Add test cases in `tests/test_suite.py` for any new feature or bug fix.
- Follow PEP 8 guidelines for Python code style.
- Maintain the Neo-Brutalist design tokens in `static/app.css` and `templates/index.html`.
- Write clear, descriptive commit messages:
  - `feat: add Freepik video search provider`
  - `fix: resolve FFmpeg aspect ratio scaling on vertical video`
  - `docs: update CapCut import tutorial`

---

## 💬 Questions & Community

- **Issues**: [GitHub Issues](https://github.com/AliRash3ed/rotodraft-suite/issues)
- **Maintainer**: Ali Rasheed (`alihouse512@gmail.com`)
- **LinkedIn**: [/in/alirasheedbhatt](https://www.linkedin.com/in/alirasheedbhatt)
