# Ingredient Scout 🍳

Ingredient Scout is an intelligent AI agent designed to simplify meal planning and grocery shopping. It automatically calculates ingredient quantities for your recipes and compares prices across major grocery platforms in India like Blinkit, Zepto, and BigBasket to find you the best deals.

## ✨ Features

- **Recipe Scaling:** Automatically scales ingredient quantities based on the number of guests.
- **Multi-Platform Comparison:** Scrapes and compares product availability and pricing from Blinkit, Zepto, and BigBasket.
- **Intelligent Mapping:** Matches required recipe quantities (e.g., 200g) with the closest available pack sizes (e.g., 250g or 500g).
- **Best Value Recommendation:** Identifies the most cost-effective platform for each ingredient.
- **AI-Powered Analysis:** Uses advanced LLMs (Gemma 4 via Ollama Cloud) to orchestrate searches and consolidate data.

## 🛠️ Tech Stack

- **Language:** Python 3.12+
- **LLM Orchestration:** [Ollama](https://ollama.com/) (Gemma 4 31B Cloud)
- **Web Scraping:** [Playwright](https://playwright.dev/) with [Playwright-Stealth](https://github.com/berstend/puppeteer-extra/tree/master/packages/extract-stealth-evasions)
- **Content Extraction:** [Trafilatura](https://trafilatura.readthedocs.io/)
- **Environment Management:** `python-dotenv`

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher.
- An Ollama Cloud API Key.
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management).

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ingredient-scout
   ```

2. **Set up the environment:**
   Create a `.env` file in the root directory and add your API key:
   ```env
   OLLAMA_CLOUD_API_KEY=your_api_key_here
   ```

3. **Install dependencies:**
   Using `uv`:
   ```bash
   uv sync
   ```
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

### Usage

Run the main agent script:
```bash
python main.py
```

Currently, the script is configured to demonstrate the LLM's ability to process queries. You can modify the `user_input` in `main.py` to ask for specific recipe ingredients and price comparisons.

## 🏗️ Project Structure

- `main.py`: The entry point containing the LLM orchestration logic and system prompts.
- `tools.py`: Contains the web scraping handles for Blinkit, Zepto, and BigBasket using Playwright.
- `pyproject.toml`: Project metadata and dependency definitions.

## 🤖 How it Works

1. **Input:** The user provides a dish and the number of guests.
2. **Scale:** The agent determines the necessary ingredients and scales the quantities.
3. **Search:** The agent parallelizes (or sequentializes) searches across grocery platforms for each ingredient.
4. **Compare:** It extracts prices and pack sizes, normalizing them for comparison.
5. **Report:** Generates a structured JSON response (or table) showing the best options to purchase.

---
*Built with ❤️ for efficient cooking.*
